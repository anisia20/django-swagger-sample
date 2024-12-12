# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets, status
import logging
from drf_yasg.utils import swagger_auto_schema

from RestApi.serializers.workserializers import WorkSerializer
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class WorkViewSet(viewsets.ModelViewSet):
    serializer_class = WorkSerializer
    swagger_auto_schema(
        operation_summary='테스트',
        operation_description='테스트 방식\n\n'
                              '테스트 데이터 Sample\n\n'
                              """
<pre>
[
    {
      "filename": "파일",
    }
]
</pre>
""",
        request_body=WorkSerializer,
        responses={
            201: "요청했던 json 데이터 그대로 echo"
        },
    )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except KeyError:
            logger.exception(msg='HTTP_400_BAD_REQUEST')
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'One of the name of request parameter is invalid'})
        except Exception as e:
            logger.exception(msg='501 NOT IMPLEMENTED')
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED, data={'message': str(e)})
