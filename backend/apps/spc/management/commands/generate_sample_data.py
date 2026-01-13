from django.core.management.base import BaseCommand
from django.db import connection
from apps.spc.models_master_data import (
    QualityItemMaster,
    QualityProcessMaster,
    QualityCharacteristicMaster,
    MeasurementInstrumentMaster,
    InspectionStandardMaster,
    QualitySyncLog,
)
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Generate sample SPC master data'

    def handle(self, *args, **options):
        self.stdout.write('Generating sample SPC master data...')

        # Check if database is available
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Database connection failed: {e}')
            )
            self.stdout.write(
                self.style.WARNING('Please ensure database is available.')
            )
            return

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        QualitySyncLog.objects.all().delete()
        InspectionStandardMaster.objects.all().delete()
        MeasurementInstrumentMaster.objects.all().delete()
        QualityCharacteristicMaster.objects.all().delete()
        QualityProcessMaster.objects.all().delete()
        QualityItemMaster.objects.all().delete()

        # Create Quality Items
        self.stdout.write('Creating Quality Items...')
        QualityItemMaster.objects.create(
            itm_id='ERP-001',
            itm_nm='배터리 셀 18650',
            itm_type='FINISHED_GOOD',
            itm_family='배터리',
            quality_grade='A',
            inspection_type='SAMPLING',
            sampling_plan='MIL-STD-105E',
            sample_size=50,
            sampling_frequency='2시간마다',
            supplier_code='SUP-001',
            supplier_nm='(주)한국배터리',
            quality_manager='홍길동',
            notes='고용량 리튬이온 배터리 셀',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 배터리 셀 18650')

        QualityItemMaster.objects.create(
            itm_id='ERP-002',
            itm_nm='배터리 셀 21700',
            itm_type='FINISHED_GOOD',
            itm_family='배터리',
            quality_grade='A',
            inspection_type='SAMPLING',
            sampling_plan='AQL=1.5',
            sample_size=50,
            sampling_frequency='2시간마다',
            supplier_code='SUP-001',
            supplier_nm='(주)한국배터리',
            quality_manager='홍길동',
            notes='고용량 리튬이온 배터리 셀',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 배터리 셀 21700')

        # Create Quality Processes
        self.stdout.write('\nCreating Quality Processes...')
        mes001 = QualityProcessMaster.objects.create(
            process_cd='MES-001',
            process_nm='배터리 셀 용접',
            process_type='WELDING',
            workcenter_cd='WC-001',
            workcenter_nm='1라인 용접공정',
            line_cd='L01',
            process_seq=10,
            process_manager='김철수',
            notes='레이저 용접 공정',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 배터리 셀 용접')

        mes002 = QualityProcessMaster.objects.create(
            process_cd='MES-002',
            process_nm='셀 조립',
            process_type='ASSEMBLY',
            workcenter_cd='WC-002',
            workcenter_nm='1라인 조립공정',
            line_cd='L01',
            process_seq=20,
            process_manager='이영희',
            notes='자동 조립 라인',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 셀 조립')

        mes004 = QualityProcessMaster.objects.create(
            process_cd='MES-004',
            process_nm='성능 시험',
            process_type='TESTING',
            workcenter_cd='WC-004',
            workcenter_nm='시험실',
            line_cd='L01',
            process_seq=40,
            process_manager='최영수',
            notes='충방전 성능 시험',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 성능 시험')

        # Create Quality Characteristics
        self.stdout.write('\nCreating Quality Characteristics...')
        item_erp001 = QualityItemMaster.objects.get(itm_id='ERP-001')

        QualityCharacteristicMaster.objects.create(
            characteristic_cd='CHAR-001',
            characteristic_nm='셀 두께',
            item=item_erp001,
            process=mes002,
            characteristic_type='DIMENSION',
            data_type='CONTINUOUS',
            unit='mm',
            lsl=18.3,
            target=18.5,
            usl=18.7,
            cpk_target=1.33,
            cpk_minimum=1.0,
            control_chart_type='XBAR_R',
            subgroup_size=5,
            measurement_method='마이크로미터',
            measurement_location='셀 중앙부',
            quality_manager='김철수',
            notes='셀 두께 치수',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 셀 두께')

        QualityCharacteristicMaster.objects.create(
            characteristic_cd='CHAR-002',
            characteristic_nm='셀 무게',
            item=item_erp001,
            process=mes002,
            characteristic_type='WEIGHT',
            data_type='CONTINUOUS',
            unit='g',
            lsl=47.5,
            target=48.0,
            usl=48.5,
            cpk_target=1.33,
            cpk_minimum=1.0,
            control_chart_type='XBAR_R',
            subgroup_size=5,
            measurement_method='전자저울',
            measurement_location='공정 출구',
            quality_manager='김철수',
            notes='셀 무게',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 셀 무게')

        # Create Measurement Instruments
        self.stdout.write('\nCreating Measurement Instruments...')
        MeasurementInstrumentMaster.objects.create(
            instrument_cd='INST-001',
            instrument_nm='디지털 마이크로미터',
            instrument_type='DIMENSION',
            manufacturer='미쯔토요',
            model_no='MDC-25MX',
            serial_no='SN-2024-001',
            measurement_range_min=0,
            measurement_range_max=25,
            resolution=0.001,
            unit='mm',
            accuracy=0.002,
            calibration_cycle=365,
            last_calibration_date=datetime.now().date() - timedelta(days=180),
            next_calibration_date=datetime.now().date() + timedelta(days=185),
            calibration_institution='한국계측연구원',
            status='ACTIVE',
            location='검사실 A',
            responsible_person='박민수',
            gage_rr_required=True,
            gage_rr_last_date=datetime.now().date() - timedelta(days=90),
            gage_rr_result='PASS',
            notes='마이크로미터',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 디지털 마이크로미터')

        MeasurementInstrumentMaster.objects.create(
            instrument_cd='INST-002',
            instrument_nm='전자저울',
            instrument_type='WEIGHT',
            manufacturer='메틀러',
            model_no='XS205',
            serial_no='SN-2024-002',
            measurement_range_min=0,
            measurement_range_max=220,
            resolution=0.0001,
            unit='g',
            accuracy=0.001,
            calibration_cycle=180,
            last_calibration_date=datetime.now().date() - timedelta(days=90),
            next_calibration_date=datetime.now().date() + timedelta(days=90),
            calibration_institution='메틀러코리아',
            status='ACTIVE',
            location='검사실 A',
            responsible_person='박민수',
            gage_rr_required=True,
            gage_rr_last_date=datetime.now().date() - timedelta(days=60),
            gage_rr_result='PASS',
            notes='정밀 전자저울',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 전자저울')

        MeasurementInstrumentMaster.objects.create(
            instrument_cd='INST-004',
            instrument_nm='내압 테스터',
            instrument_type='TEST_EQUIPMENT',
            manufacturer='일본계측기',
            model_no='JP-200',
            serial_no='SN-2024-004',
            measurement_range_min=0,
            measurement_range_max=50,
            resolution=0.1,
            unit='kgf/cm²',
            accuracy=0.2,
            calibration_cycle=180,
            last_calibration_date=datetime.now().date() - timedelta(days=200),
            next_calibration_date=datetime.now().date() - timedelta(days=20),
            calibration_institution='한국계측연구원',
            status='CALIBRATION_DUE',
            location='시험실',
            responsible_person='최영수',
            gage_rr_required=True,
            gage_rr_last_date=datetime.now().date() - timedelta(days=150),
            gage_rr_result='PASS',
            notes='내압 테스터 - 보정 만료됨',
            active_yn='Y',
        )
        self.stdout.write('  - Created: 내압 테스터')

        # Create Sync Logs
        self.stdout.write('\nCreating Sync Logs...')
        QualitySyncLog.objects.create(
            sync_type='ITEM',
            sync_source='ERP',
            sync_status='SUCCESS',
            records_total=5,
            records_success=5,
            records_failed=0,
            error_message='',
            sync_start_ts=datetime.now() - timedelta(days=7),
            sync_end_ts=datetime.now() - timedelta(days=7) + timedelta(seconds=2),
            sync_ts=datetime.now() - timedelta(days=7),
        )
        self.stdout.write('  - Created: ITEM (SUCCESS)')

        QualitySyncLog.objects.create(
            sync_type='PROCESS',
            sync_source='MES',
            sync_status='SUCCESS',
            records_total=5,
            records_success=5,
            records_failed=0,
            error_message='',
            sync_start_ts=datetime.now() - timedelta(days=6),
            sync_end_ts=datetime.now() - timedelta(days=6) + timedelta(seconds=3),
            sync_ts=datetime.now() - timedelta(days=6),
        )
        self.stdout.write('  - Created: PROCESS (SUCCESS)')

        QualitySyncLog.objects.create(
            sync_type='INSTRUMENT',
            sync_source='LEGACY',
            sync_status='PARTIAL',
            records_total=5,
            records_success=4,
            records_failed=1,
            error_message='INST-004: 캘리브레이션 데이터 불일치',
            sync_start_ts=datetime.now() - timedelta(days=5),
            sync_end_ts=datetime.now() - timedelta(days=5) + timedelta(seconds=5),
            sync_ts=datetime.now() - timedelta(days=5),
        )
        self.stdout.write('  - Created: INSTRUMENT (PARTIAL)')

        self.stdout.write(self.style.SUCCESS('\nSample data generation complete!'))
        self.stdout.write('\nSummary:')
        self.stdout.write(f'  - Quality Items: {QualityItemMaster.objects.count()}')
        self.stdout.write(f'  - Quality Processes: {QualityProcessMaster.objects.count()}')
        self.stdout.write(f'  - Quality Characteristics: {QualityCharacteristicMaster.objects.count()}')
        self.stdout.write(f'  - Measurement Instruments: {MeasurementInstrumentMaster.objects.count()}')
        self.stdout.write(f'  - Inspection Standards: {InspectionStandardMaster.objects.count()}')
        self.stdout.write(f'  - Sync Logs: {QualitySyncLog.objects.count()}')
