# Generated manually for STEP 3: UnplannedReason model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aps', '0003_add_execution_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnplannedReason',
            fields=[
                ('reason_id', models.AutoField(primary_key=True, serialize=False)),
                ('wo_no', models.CharField(db_index=True, max_length=30)),
                ('itm_id', models.CharField(blank=True, max_length=50, null=True)),
                ('mc_cd', models.CharField(blank=True, max_length=20, null=True)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('priority', models.IntegerField(default=0)),
                ('reason_code', models.CharField(
                    choices=[
                        ('CAPACITY_SHORTAGE', '자원 부족 - 가용시간 대비 작업량 초과'),
                        ('CALENDAR_CONFLICT', '캘린더 충돌 - 근무시간/휴일로 배정 불가'),
                        ('PRIORITY_LOSS', '우선순위 손실 - 낮은 우선순위로 후순위 배정'),
                        ('DATA_MISSING', '데이터 누락 - Routing/Operation/Resource 정보 없음'),
                    ],
                    db_index=True,
                    max_length=30
                )),
                ('status', models.CharField(
                    choices=[
                        ('UNPLANNED', '미계획 - 스케줄에 배정되지 않음'),
                        ('DELAYED', '지연 - 납기일 초과'),
                    ],
                    default='UNPLANNED',
                    max_length=20
                )),
                ('delay_hours', models.FloatField(
                    default=0,
                    help_text='납기 대비 지연 시간 (시간 단위)'
                )),
                ('confidence', models.FloatField(
                    default=0,
                    help_text='원인 분류 신뢰도 (0~1)'
                )),
                ('explanation', models.TextField(
                    blank=True,
                    help_text='원인에 대한 상세 설명',
                    null=True
                )),
                ('analysis_data', models.JSONField(
                    blank=True,
                    help_text='추가 분석 메트릭 (capacity_ratio, avg_priority 등)',
                    null=True
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('scenario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='unplanned_reasons',
                    to='aps.scenario'
                )),
            ],
            options={
                'verbose_name': '미계획 원인',
                'verbose_name_plural': '미계획 원인 분석',
                'db_table': 'unplanned_reason',
                'ordering': ['-created_at', 'scenario', 'reason_code'],
            },
        ),
        migrations.AddIndex(
            model_name='unplannedreason',
            index=models.Index(
                fields=['scenario', 'reason_code'],
                name='ix_unplanned_scenario_code'
            ),
        ),
        migrations.AddIndex(
            model_name='unplannedreason',
            index=models.Index(
                fields=['wo_no', 'created_at'],
                name='ix_unplanned_wo_ts'
            ),
        ),
        migrations.AddIndex(
            model_name='unplannedreason',
            index=models.Index(
                fields=['status', 'reason_code'],
                name='ix_unplanned_status_code'
            ),
        ),
    ]
