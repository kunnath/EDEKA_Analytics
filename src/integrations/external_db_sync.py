"""
External database integration module for the EDEKA analytics application.

This module provides functionality to sync data from an external database
to the internal database used for analytics.
"""
import os
import time
import pandas as pd
from datetime import datetime
import traceback
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError

from src.utils.db_utils import (
    get_internal_db_engine,
    get_external_db_engine,
    get_db_session,
    load_config
)
from src.utils.logger import logger
from src.utils.mock_data import get_mock_data
from src.models.database import SyncLog
from src.utils.logger import logger
from src.models.database import SyncLog

class DatabaseSyncManager:
    """
    Manager class for synchronizing data between external and internal databases.
    """
    
    def __init__(self):
        """Initialize the sync manager with database connections and configuration."""
        self.config = load_config()
        self.internal_engine = get_internal_db_engine()
        self.external_engine = get_external_db_engine()
        self.column_mappings = self.config['column_mappings']
        self.transformations = self.config['transformations']
        self.sync_config = self.config['sync']
        
    def _get_last_sync_timestamp(self, table_name):
        """Get the timestamp of the last successful sync for a table."""
        with get_db_session(self.internal_engine) as session:
            latest_sync = (
                session.query(SyncLog)
                .filter(SyncLog.table_name == table_name, SyncLog.status == 'success')
                .order_by(SyncLog.sync_end.desc())
                .first()
            )
            
            if latest_sync:
                return latest_sync.sync_end
            return None
    
    def _log_sync_start(self, table_name):
        """Log the start of a sync operation."""
        with get_db_session(self.internal_engine) as session:
            sync_log = SyncLog(
                sync_start=datetime.now(),
                table_name=table_name,
                records_fetched=0,
                records_inserted=0,
                records_updated=0,
                records_failed=0,
                status='in_progress'
            )
            session.add(sync_log)
            session.commit()
            return sync_log.log_id
    
    def _log_sync_end(self, log_id, records_fetched, records_inserted, records_updated, records_failed, error_message=None):
        """Log the end of a sync operation."""
        with get_db_session(self.internal_engine) as session:
            sync_log = session.query(SyncLog).get(log_id)
            if sync_log:
                sync_log.sync_end = datetime.now()
                sync_log.records_fetched = records_fetched
                sync_log.records_inserted = records_inserted
                sync_log.records_updated = records_updated
                sync_log.records_failed = records_failed
                sync_log.status = 'failed' if error_message else 'success'
                sync_log.error_message = error_message
                session.commit()
    
    def _fetch_external_data(self, table_name, last_sync_time=None):
        """Fetch data from the external database."""
        # Check if in development mode
        dev_mode = os.getenv('EDEKA_DEV_MODE', 'false').lower() == 'true'
        
        if dev_mode:
            # Use mock data in development mode
            logger.info(f"Using mock data for {table_name} in development mode")
            return get_mock_data(table_name)
            
        # Production mode - connect to real database
        table_config = self.column_mappings.get(table_name)
        if not table_config:
            raise ValueError(f"No configuration found for table {table_name}")
        
        external_table = table_config['external_table']
        mappings = table_config['mappings']
        
        # Build column selection
        columns = [f"{col} as {ext_col}" for ext_col, col in mappings.items()]
        columns_str = ", ".join(columns)
        
        # Build query
        query = f"SELECT {columns_str} FROM {external_table}"
        
        # Add incremental sync condition if enabled
        if self.sync_config['incremental'] and last_sync_time:
            timestamp_col = self.sync_config['timestamp_column']
            query += f" WHERE {timestamp_col} > :last_sync_time"
            params = {'last_sync_time': last_sync_time}
        else:
            params = {}
        
        # Add batch limit if specified
        batch_size = self.sync_config.get('batch_size')
        if batch_size:
            query += f" LIMIT {batch_size}"
        
        # Execute query
        with get_db_session(self.external_engine) as session:
            result = session.execute(text(query), params)
            data = result.fetchall()
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        return df
    
    def _transform_data(self, df, table_name):
        """Apply transformations to the data."""
        if df.empty:
            return df
        
        # Apply date transformations
        date_columns = self.transformations.get('date_columns', [])
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        # Apply category mappings if applicable
        category_mapping = self.transformations.get('category_mapping', {})
        if table_name == 'products' and 'category_id' in df.columns:
            df['category_id'] = df['category_id'].map(lambda x: category_mapping.get(x, x))
        
        return df
    
    def _insert_or_update_data(self, df, table_name):
        """Insert or update data in the internal database."""
        if df.empty:
            logger.info(f"No data to insert for {table_name}")
            return 0, 0, 0
        
        records_inserted = 0
        records_updated = 0
        records_failed = 0
        
        # Get primary key for the table to determine insert vs update
        primary_keys = {
            'sales': 'bill_id',
            'products': 'product_id',
            'customers': 'customer_id',
            'stores': 'store_id'
        }
        
        primary_key = primary_keys.get(table_name)
        if not primary_key:
            raise ValueError(f"Primary key not defined for table {table_name}")
        
        # Process each record
        with get_db_session(self.internal_engine) as session:
            for _, row in df.iterrows():
                try:
                    # Convert row to dict
                    record = row.to_dict()
                    
                    # Check if record exists
                    query = text(f"SELECT 1 FROM {table_name} WHERE {primary_key} = :pk_value")
                    result = session.execute(query, {'pk_value': record[primary_key]})
                    exists = result.fetchone() is not None
                    
                    if exists:
                        # Update existing record
                        set_clause = ", ".join([f"{col} = :{col}" for col in record.keys() if col != primary_key])
                        update_query = text(f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = :pk_value")
                        params = {**record, 'pk_value': record[primary_key]}
                        session.execute(update_query, params)
                        records_updated += 1
                    else:
                        # Insert new record
                        columns = ", ".join(record.keys())
                        placeholders = ", ".join([f":{col}" for col in record.keys()])
                        insert_query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
                        session.execute(insert_query, record)
                        records_inserted += 1
                
                except Exception as e:
                    logger.error(f"Error processing record: {e}")
                    records_failed += 1
                    continue
            
            # Commit the transaction
            session.commit()
        
        return records_inserted, records_updated, records_failed
    
    def sync_table(self, table_name):
        """Sync a specific table from external to internal database."""
        logger.info(f"Starting sync for table: {table_name}")
        
        # Log sync start
        log_id = self._log_sync_start(table_name)
        
        records_fetched = 0
        records_inserted = 0
        records_updated = 0
        records_failed = 0
        error_message = None
        
        try:
            # Get last sync time if incremental sync is enabled
            last_sync_time = None
            if self.sync_config['incremental']:
                last_sync_time = self._get_last_sync_timestamp(table_name)
                logger.info(f"Last sync time for {table_name}: {last_sync_time}")
            
            # Fetch data from external database
            df = self._fetch_external_data(table_name, last_sync_time)
            records_fetched = len(df)
            logger.info(f"Fetched {records_fetched} records from external database")
            
            if not df.empty:
                # Transform data
                df = self._transform_data(df, table_name)
                logger.info(f"Transformed data for {table_name}")
                
                # Insert or update data
                inserted, updated, failed = self._insert_or_update_data(df, table_name)
                records_inserted = inserted
                records_updated = updated
                records_failed = failed
                logger.info(f"Inserted: {inserted}, Updated: {updated}, Failed: {failed}")
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error syncing table {table_name}: {error_message}")
            logger.error(traceback.format_exc())
        
        # Log sync end
        self._log_sync_end(log_id, records_fetched, records_inserted, records_updated, records_failed, error_message)
        
        logger.info(f"Completed sync for table: {table_name}")
        return records_fetched, records_inserted, records_updated, records_failed
    
    def sync_external_data(self):
        """Sync all configured tables from external to internal database."""
        logger.info("Starting external data sync process")
        
        total_fetched = 0
        total_inserted = 0
        total_updated = 0
        total_failed = 0
        
        start_time = time.time()
        
        # Sync each table in the correct order to satisfy foreign key constraints
        # First sync stores, then products, then customers, then sales
        ordered_tables = ['stores', 'products', 'customers', 'sales']
        for table_name in ordered_tables:
            if table_name in self.sync_config['tables_to_sync'] or table_name == 'stores':
                fetched, inserted, updated, failed = self.sync_table(table_name)
                total_fetched += fetched
                total_inserted += inserted
                total_updated += updated
                total_failed += failed
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Log summary
        logger.info(f"Sync completed in {duration:.2f} seconds")
        logger.info(f"Total records fetched: {total_fetched}")
        logger.info(f"Total records inserted: {total_inserted}")
        logger.info(f"Total records updated: {total_updated}")
        logger.info(f"Total records failed: {total_failed}")
        
        return {
            'fetched': total_fetched,
            'inserted': total_inserted,
            'updated': total_updated,
            'failed': total_failed,
            'duration': duration
        }
