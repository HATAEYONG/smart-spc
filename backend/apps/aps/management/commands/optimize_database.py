"""
Django Management Command: Optimize Database Performance

This command performs comprehensive database optimization including:
- Creating indexes for frequently queried fields
- Analyzing query performance
- Generating optimization recommendations
- Creating materialized views (if needed)
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.apps import apps
import time


class Command(BaseCommand):
    help = 'Optimize database performance with indexes and analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analyze current database performance',
        )
        parser.add_argument(
            '--create-indexes',
            action='store_true',
            help='Create recommended indexes',
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Run VACUUM ANALYZE on PostgreSQL',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all optimization steps',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Database Performance Optimization'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        if options['all']:
            options['analyze'] = True
            options['create_indexes'] = True
            options['vacuum'] = True

        if options['analyze']:
            self.analyze_performance()

        if options['create_indexes']:
            self.create_indexes()

        if options['vacuum']:
            self.vacuum_database()

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Optimization Complete'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def analyze_performance(self):
        """Analyze current database performance"""
        self.stdout.write('\n[1/3] Analyzing Database Performance...\n')

        with connection.cursor() as cursor:
            # Table sizes
            self.stdout.write(self.style.WARNING('\nTable Sizes:'))
            cursor.execute("""
                SELECT
                    schemaname || '.' || tablename AS table_name,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) -
                                   pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10;
            """)
            for row in cursor.fetchall():
                self.stdout.write(f"  {row[0]:<50} Total: {row[1]:<10} Table: {row[2]:<10} Indexes: {row[3]}")

            # Index usage
            self.stdout.write(self.style.WARNING('\nIndex Usage Statistics:'))
            cursor.execute("""
                SELECT
                    schemaname || '.' || tablename AS table_name,
                    indexname,
                    idx_scan AS index_scans,
                    idx_tup_read AS tuples_read,
                    idx_tup_fetch AS tuples_fetched
                FROM pg_stat_user_indexes
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY idx_scan DESC
                LIMIT 10;
            """)
            for row in cursor.fetchall():
                self.stdout.write(f"  {row[0]:<40} {row[1]:<30} Scans: {row[2]}")

            # Missing indexes (seq scans on large tables)
            self.stdout.write(self.style.WARNING('\nTables with High Sequential Scans (may need indexes):'))
            cursor.execute("""
                SELECT
                    schemaname || '.' || tablename AS table_name,
                    seq_scan,
                    seq_tup_read,
                    idx_scan,
                    n_live_tup
                FROM pg_stat_user_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                  AND seq_scan > 100
                  AND n_live_tup > 1000
                ORDER BY seq_scan DESC
                LIMIT 10;
            """)
            for row in cursor.fetchall():
                self.stdout.write(f"  {row[0]:<50} Seq Scans: {row[1]:<10} Rows: {row[4]}")

            # Cache hit ratio
            self.stdout.write(self.style.WARNING('\nCache Hit Ratio:'))
            cursor.execute("""
                SELECT
                    round((sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read))) * 100, 2) as cache_hit_ratio
                FROM pg_statio_user_tables
                WHERE heap_blks_hit + heap_blks_read > 0;
            """)
            ratio = cursor.fetchone()[0]
            if ratio:
                self.stdout.write(f"  Cache Hit Ratio: {ratio}%")
                if ratio < 90:
                    self.stdout.write(self.style.WARNING(f"  ⚠️  Low cache hit ratio. Consider increasing shared_buffers."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Good cache hit ratio"))

            # Unused indexes
            self.stdout.write(self.style.WARNING('\nUnused Indexes (candidates for removal):'))
            cursor.execute("""
                SELECT
                    schemaname || '.' || tablename AS table_name,
                    indexname,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||indexname)) AS index_size
                FROM pg_stat_user_indexes
                WHERE idx_scan = 0
                  AND indexname NOT LIKE '%pkey'
                  AND schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY pg_relation_size(schemaname||'.'||indexname) DESC
                LIMIT 10;
            """)
            unused = cursor.fetchall()
            if unused:
                for row in unused:
                    self.stdout.write(f"  {row[0]:<40} {row[1]:<30} Size: {row[2]}")
            else:
                self.stdout.write(self.style.SUCCESS(f"  ✓ No unused indexes found"))

    def create_indexes(self):
        """Create recommended indexes for APS application"""
        self.stdout.write('\n[2/3] Creating Recommended Indexes...\n')

        indexes = [
            # ERP Product indexes
            {
                'name': 'idx_erp_product_code',
                'table': 'erp_product',
                'columns': ['code'],
                'description': 'Product lookup by code'
            },
            {
                'name': 'idx_erp_product_name',
                'table': 'erp_product',
                'columns': ['name'],
                'description': 'Product search by name'
            },

            # ERP BOM indexes
            {
                'name': 'idx_erp_bom_product_id',
                'table': 'erp_bom',
                'columns': ['product_id'],
                'description': 'BOM lookup by product'
            },
            {
                'name': 'idx_erp_bom_parent_id',
                'table': 'erp_bom',
                'columns': ['parent_id'],
                'description': 'BOM hierarchy lookup'
            },

            # ERP Routing indexes
            {
                'name': 'idx_erp_routing_product_id',
                'table': 'erp_routing',
                'columns': ['product_id'],
                'description': 'Routing lookup by product'
            },
            {
                'name': 'idx_erp_routing_resource_id',
                'table': 'erp_routing',
                'columns': ['resource_id'],
                'description': 'Routing lookup by resource'
            },
            {
                'name': 'idx_erp_routing_op_seq',
                'table': 'erp_routing',
                'columns': ['product_id', 'op_seq'],
                'description': 'Routing operations order'
            },

            # ERP Resource indexes
            {
                'name': 'idx_erp_resource_code',
                'table': 'erp_resource',
                'columns': ['code'],
                'description': 'Resource lookup by code'
            },
            {
                'name': 'idx_erp_resource_type',
                'table': 'erp_resource',
                'columns': ['resource_type'],
                'description': 'Resource filtering by type'
            },

            # APS Scenario indexes
            {
                'name': 'idx_aps_scenario_status',
                'table': 'aps_scenario',
                'columns': ['status'],
                'description': 'Scenario filtering by status'
            },
            {
                'name': 'idx_aps_scenario_created_at',
                'table': 'aps_scenario',
                'columns': ['created_at'],
                'description': 'Scenario sorting by creation time'
            },
            {
                'name': 'idx_aps_scenario_start_date',
                'table': 'aps_scenario',
                'columns': ['start_date'],
                'description': 'Scenario filtering by start date'
            },

            # APS Order indexes
            {
                'name': 'idx_aps_order_scenario_id',
                'table': 'aps_order',
                'columns': ['scenario_id'],
                'description': 'Order lookup by scenario'
            },
            {
                'name': 'idx_aps_order_product_id',
                'table': 'aps_order',
                'columns': ['product_id'],
                'description': 'Order lookup by product'
            },
            {
                'name': 'idx_aps_order_due_date',
                'table': 'aps_order',
                'columns': ['due_date'],
                'description': 'Order filtering by due date'
            },
            {
                'name': 'idx_aps_order_scenario_due',
                'table': 'aps_order',
                'columns': ['scenario_id', 'due_date'],
                'description': 'Order sorting within scenario'
            },

            # APS Operation indexes
            {
                'name': 'idx_aps_operation_order_id',
                'table': 'aps_operation',
                'columns': ['order_id'],
                'description': 'Operation lookup by order'
            },
            {
                'name': 'idx_aps_operation_resource_id',
                'table': 'aps_operation',
                'columns': ['resource_id'],
                'description': 'Operation lookup by resource'
            },
            {
                'name': 'idx_aps_operation_start_dt',
                'table': 'aps_operation',
                'columns': ['start_dt'],
                'description': 'Operation timeline queries'
            },
            {
                'name': 'idx_aps_operation_resource_start',
                'table': 'aps_operation',
                'columns': ['resource_id', 'start_dt'],
                'description': 'Resource schedule queries'
            },

            # Composite indexes for common queries
            {
                'name': 'idx_aps_operation_order_seq',
                'table': 'aps_operation',
                'columns': ['order_id', 'op_seq'],
                'description': 'Operation order and sequence'
            },
        ]

        with connection.cursor() as cursor:
            for index in indexes:
                try:
                    # Check if index already exists
                    cursor.execute("""
                        SELECT 1 FROM pg_indexes
                        WHERE indexname = %s;
                    """, [index['name']])

                    if cursor.fetchone():
                        self.stdout.write(f"  ⊘ {index['name']} - Already exists")
                        continue

                    # Create index
                    columns_str = ', '.join(index['columns'])
                    sql = f"CREATE INDEX CONCURRENTLY {index['name']} ON {index['table']} ({columns_str});"

                    self.stdout.write(f"  Creating {index['name']}...")
                    start_time = time.time()
                    cursor.execute(sql)
                    elapsed = time.time() - start_time

                    self.stdout.write(self.style.SUCCESS(
                        f"  ✓ {index['name']} created in {elapsed:.2f}s - {index['description']}"
                    ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"  ✗ Failed to create {index['name']}: {str(e)}"
                    ))

            # Create partial indexes for specific conditions
            self.stdout.write(self.style.WARNING('\nCreating Partial Indexes...'))

            partial_indexes = [
                {
                    'name': 'idx_aps_scenario_active',
                    'sql': "CREATE INDEX CONCURRENTLY idx_aps_scenario_active ON aps_scenario (created_at) WHERE status IN ('pending', 'running');"
                },
                {
                    'name': 'idx_aps_order_not_scheduled',
                    'sql': "CREATE INDEX CONCURRENTLY idx_aps_order_not_scheduled ON aps_order (scenario_id) WHERE scheduled_dt IS NULL;"
                },
            ]

            for pindex in partial_indexes:
                try:
                    cursor.execute(f"SELECT 1 FROM pg_indexes WHERE indexname = '{pindex['name']}';")
                    if cursor.fetchone():
                        self.stdout.write(f"  ⊘ {pindex['name']} - Already exists")
                        continue

                    cursor.execute(pindex['sql'])
                    self.stdout.write(self.style.SUCCESS(f"  ✓ {pindex['name']} created"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Failed to create {pindex['name']}: {str(e)}"))

    def vacuum_database(self):
        """Run VACUUM ANALYZE to optimize PostgreSQL"""
        self.stdout.write('\n[3/3] Running VACUUM ANALYZE...\n')

        tables = [
            'erp_product',
            'erp_bom',
            'erp_routing',
            'erp_resource',
            'aps_scenario',
            'aps_order',
            'aps_operation',
        ]

        # Note: VACUUM cannot run inside a transaction block
        # We need to use autocommit mode
        connection.cursor().execute('COMMIT')

        with connection.cursor() as cursor:
            for table in tables:
                try:
                    self.stdout.write(f"  Analyzing {table}...")
                    cursor.execute(f"VACUUM ANALYZE {table};")
                    self.stdout.write(self.style.SUCCESS(f"  ✓ {table} analyzed"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Failed to analyze {table}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('\n✓ Database optimization complete'))
