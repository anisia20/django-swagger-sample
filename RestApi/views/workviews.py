# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets, status
import logging
from drf_yasg.utils import swagger_auto_schema
import pandas as pd
from azure.core.credentials import AzureKeyCredential
import openai
from drf_yasg import openapi

from RestApi.model import Work
from RestApi.serializers.workserializers import WorkSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

logger = logging.getLogger(__name__)

class WorkViewSet(viewsets.ModelViewSet):
    queryset = Work.objects.all()  # QuerySet을 명시적으로 정의
    swagger_fake_view = True
    serializer_class = WorkSerializer
    parser_classes = [MultiPartParser]  # 파일 업로드를 위해 설정

    swagger_auto_schema(
        operation_summary="파일 업로드 및 처리",
        operation_description="엑셀 파일을 업로드하고 RFM 분석 결과를 반환합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file': openapi.Schema(type=openapi.TYPE_FILE, description="엑셀 파일"),
            },
            required=['file'],
        ),
        responses={
            201: openapi.Response("RFM 분석 결과", examples={
                "application/json": {
                    "message": "RFM report generated successfully",
                    "report": "Report content here"
                }
            }),
            400: "잘못된 요청",
        }
    )
    def create(self, request, *args, **kwargs):
        # if getattr(self, 'swagger_fake_view', False):
        #     return  # 스키마 생성 중이라면 아무 작업도 수행하지 않
        try:
            # 엑셀 파일 가져오기
            excel_file = request.FILES.get('file')
            if not excel_file:
                return Response({'message': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

            # 엑셀 파일 파싱
            df = pd.read_excel(excel_file)
            data = self._prepare_data(df)

            # Azure GPT API 호출
            gpt_response = self._request_gpt(data)

            return Response({
                'message': 'RFM report generated successfully',
                'report': gpt_response
            }, status=status.HTTP_201_CREATED)

        except KeyError:
            logger.exception(msg='HTTP_400_BAD_REQUEST')
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'One of the names of request parameter is invalid'})
        except Exception as e:
            logger.exception(msg='501 NOT IMPLEMENTED')
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED, data={'message': str(e)})

    def _prepare_data(self, df):
        # 데이터 변환 로직
        records = df.to_dict(orient='records')
        formatted_data = []
        for record in records:
            time = record.get('시간', 'Unknown Time')
            person = record.get('이름', 'Unknown Person')
            product = record.get('제품', 'Unknown Product')
            quantity = record.get('수량', 0)
            formatted_data.append(f"At {time}, {person} bought {quantity} {product}.")
        return "\n".join(formatted_data)

    def _request_gpt(self, data):
        # Azure OpenAI 설정
        openai.api_type = "azure"
        openai.api_base = "https://your-resource-name.openai.azure.com/"
        openai.api_version = "2023-05-15"  # Azure에서 사용하는 OpenAI API 버전
        openai.api_key = "your-azure-openai-key"

        # GPT 모델 요청
        response = openai.ChatCompletion.create(
            engine="your-deployment-name",  # Azure에 배포된 모델 이름
            messages=[
                {"role": "system", "content": "You are an expert in generating RFM analysis reports."},
                {"role": "user", "content": "Generate an RFM report based on the sales data."}
            ],
            max_tokens=500
        )

        print(response['choices'][0]['message']['content'])