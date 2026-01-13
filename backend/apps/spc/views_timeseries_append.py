

class TimeSeriesAnalysisViewSet(viewsets.GenericViewSet):
    """
    시계열 분석 API (Time Series Analysis)
    추세 분석, 예측, 이상 감지, 예지 보전 기능 제공
    """
    queryset = Product.objects.all()  # Dummy queryset

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        종합 시계열 분석
        추세, 계절성, 분해, 예측, 이상 감지를 모두 포함
        """
        serializer = TimeSeriesAnalysisRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_id = data['product_id']
        days = data['days']
        forecast_steps = data['forecast_steps']

        try:
            from .services.time_series_analysis import TimeSeriesService

            service = TimeSeriesService()
            result = service.analyze_product_timeseries(
                product_id=product_id,
                days=days,
                forecast_steps=forecast_steps
            )

            return Response(result)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Time series analysis error: {str(e)}")
            return Response(
                {'error': f'Analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def forecast(self, request):
        """
        시계열 예측
        단일 예측 방법 사용 (MA, ES, LT, COMBINED)
        """
        serializer = ForecastRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_id = data['product_id']
        days = data['days']
        forecast_steps = data['forecast_steps']
        method = data['method']

        try:
            from .services.time_series_analysis import ForecastEngine

            # 제품 정보 조회
            product = Product.objects.get(id=product_id)

            # 측정 데이터 조회
            start_date = timezone.now() - timedelta(days=days)
            measurements_qs = QualityMeasurement.objects.filter(
                product_id=product_id,
                measured_at__gte=start_date
            ).order_by('measured_at')

            if measurements_qs.count() < 5:
                return Response(
                    {'error': '최소 5개 이상의 측정 데이터가 필요합니다'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            measurements = list(measurements_qs.values_list('measurement_value', flat=True))
            timestamps = list(measurements_qs.values_list('measured_at', flat=True))

            # 예측 엔진 생성
            engine = ForecastEngine()

            # 예측 방법별 실행
            if method == 'MA':
                forecast_data = engine.simple_ma_forecast(
                    measurements,
                    forecast_steps=forecast_steps,
                    window_size=min(7, len(measurements) // 2)
                )
            elif method == 'ES':
                forecast_data = engine.exponential_smoothing_forecast(
                    measurements,
                    forecast_steps=forecast_steps,
                    alpha=0.3
                )
            elif method == 'LT':
                forecast_data = engine.linear_trend_forecast(
                    measurements,
                    forecast_steps=forecast_steps
                )
            else:  # COMBINED
                forecast_data = engine.combined_forecast(
                    measurements,
                    forecast_steps=forecast_steps
                )

            # 예측 날짜 계산
            last_timestamp = timestamps[-1]
            forecast_dates = []
            for i in range(forecast_steps):
                next_time = last_timestamp + timedelta(hours=i * 8)  # 8시간 간격 가정
                forecast_dates.append(next_time.isoformat())

            # 응답 생성
            response = {
                'product_id': product_id,
                'product_code': product.product_code,
                'method': method,
                'forecast_steps': forecast_steps,
                'forecast_values': forecast_data['forecast_values'],
                'forecast_dates': forecast_dates,
                'accuracy_metrics': forecast_data.get('accuracy_metrics', {}),
                'forecasted_at': timezone.now().isoformat()
            }

            # 신뢰 구간 추가 (있는 경우)
            if 'confidence_interval' in forecast_data:
                response['confidence_interval'] = forecast_data['confidence_interval']

            return Response(response)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Forecast error: {str(e)}")
            return Response(
                {'error': f'Forecast failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def maintenance_predict(self, request):
        """
        예지 보전 분석
        설비 건전도, 열화 추세, 고장 예측 제공
        """
        serializer = PredictiveMaintenanceRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_id = data['product_id']
        days = data['days']

        try:
            from .services.time_series_analysis import TimeSeriesService

            service = TimeSeriesService()
            result = service.get_maintenance_prediction(
                product_id=product_id,
                days=days
            )

            return Response(result)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Maintenance prediction error: {str(e)}")
            return Response(
                {'error': f'Prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def detect_anomalies(self, request):
        """
        이상 감지
        통계적 방법 (Z-score) 및 패턴 기반 이상 감지
        """
        serializer = AnomalyDetectionRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_id = data['product_id']
        days = data['days']
        threshold = data['threshold']

        try:
            from .services.time_series_analysis import AnomalyDetector

            # 제품 정보 조회
            product = Product.objects.get(id=product_id)

            # 측정 데이터 조회
            start_date = timezone.now() - timedelta(days=days)
            end_date = timezone.now()

            measurements_qs = QualityMeasurement.objects.filter(
                product_id=product_id,
                measured_at__gte=start_date,
                measured_at__lte=end_date
            ).order_by('measured_at')

            if measurements_qs.count() < 3:
                return Response(
                    {'error': '최소 3개 이상의 측정 데이터가 필요합니다'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            measurements = list(measurements_qs.values_list('measurement_value', flat=True))

            # 이상 감지기 생성
            detector = AnomalyDetector()

            # 통계적 이상 감지
            statistical_anomalies = detector.detect_statistical_anomalies(
                measurements,
                threshold=threshold
            )

            # 패턴 기반 이상 감지
            pattern_anomalies = detector.detect_pattern_anomalies(measurements)

            # 이상 데이터에 인덱스와 타임스탬프 추가
            measurements_with_timestamp = measurements_qs.values('id', 'measurement_value', 'measured_at')

            anomalies_list = []
            for idx, measurement in enumerate(measurements_with_timestamp):
                measurement_idx = idx

                # 통계적 이상 확인
                stat_anomaly = next(
                    (a for a in statistical_anomalies if a['index'] == measurement_idx),
                    None
                )

                # 패턴 기반 이상 확인
                pattern_anomaly = next(
                    (a for a in pattern_anomalies if a['index'] == measurement_idx),
                    None
                )

                if stat_anomaly or pattern_anomaly:
                    anomaly_info = {
                        'id': measurement['id'],
                        'value': measurement['measurement_value'],
                        'measured_at': measurement['measured_at'].isoformat(),
                    }

                    if stat_anomaly:
                        anomaly_info['statistical'] = {
                            'z_score': stat_anomaly['z_score'],
                            'severity': stat_anomaly['severity']
                        }

                    if pattern_anomaly:
                        anomaly_info['pattern'] = {
                            'type': pattern_anomaly['type'],
                            'description': pattern_anomaly['description']
                        }

                    # 이상 점수 계산
                    anomaly_score = detector.calculate_anomaly_score(
                        measurement['measurement_value'],
                        measurements
                    )
                    anomaly_info['anomaly_score'] = anomaly_score

                    anomalies_list.append(anomaly_info)

            # 응답 생성
            response = {
                'product_id': product_id,
                'product_code': product.product_code,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_data_points': len(measurements),
                'anomalies': anomalies_list,
                'anomaly_count': len(anomalies_list),
                'anomaly_rate': round(len(anomalies_list) / len(measurements) * 100, 2) if measurements else 0,
                'detection_method': 'statistical_and_pattern',
                'threshold': threshold,
                'detected_at': timezone.now().isoformat()
            }

            return Response(response)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}")
            return Response(
                {'error': f'Detection failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def capabilities(self, request):
        """
        시계열 분석 기능 안내
        """
        return Response({
            'name': 'Time Series Analysis Service',
            'version': '1.0.0',
            'description': '시계열 분석, 예측, 이상 감지, 예지 보전 기능을 제공합니다',
            'endpoints': {
                'analyze': {
                    'method': 'POST',
                    'description': '종합 시계열 분석 (추세, 계절성, 분해, 예측, 이상 감지)',
                    'parameters': {
                        'product_id': '제품 ID (필수)',
                        'days': '분석 기간 (일, 기본값: 30)',
                        'forecast_steps': '예측 스텝 수 (기본값: 5)'
                    }
                },
                'forecast': {
                    'method': 'POST',
                    'description': '시계열 예측',
                    'parameters': {
                        'product_id': '제품 ID (필수)',
                        'days': '학습 데이터 기간 (일, 기본값: 30)',
                        'forecast_steps': '예측 스텝 수 (기본값: 5)',
                        'method': '예측 방법 (MA, ES, LT, COMBINED, 기본값: COMBINED)'
                    }
                },
                'maintenance_predict': {
                    'method': 'POST',
                    'description': '예지 보전 분석',
                    'parameters': {
                        'product_id': '제품 ID (필수)',
                        'days': '분석 기간 (일, 기본값: 30)'
                    }
                },
                'detect_anomalies': {
                    'method': 'POST',
                    'description': '이상 감지',
                    'parameters': {
                        'product_id': '제품 ID (필수)',
                        'days': '분석 기간 (일, 기본값: 30)',
                        'threshold': 'Z-score 임계값 (기본값: 3.0)'
                    }
                }
            },
            'forecast_methods': {
                'MA': '이동평균 (Moving Average) - 안정적인 데이터에 적합',
                'ES': '지수평활 (Exponential Smoothing) - 최근 데이터에 가중치',
                'LT': '선형추세 (Linear Trend) - 추세가 명확한 경우',
                'COMBINED': '앙상블 (Combined) - 여러 방법 결합 (권장)'
            },
            'anomaly_detection': {
                'statistical': 'Z-score 기반 통계적 이상 감지',
                'pattern': 'Spike, Trend Shift 등 패턴 기반 감지',
                'anomaly_score': '0-100 사이의 이상 점수'
            },
            'predictive_maintenance': {
                'equipment_health': '설비 건전도 점수 (0-100)',
                'degradation_trend': '열화 추세 분석',
                'failure_prediction': '규격 벗어남 예측 시점'
            }
        })
