class BaseResponse:
    def __init__(
        self,
        code=200,
        message='success',
        data=None,
        page_num=None,
        page_size=0,
        total=0,
    ) -> None:
        self.json = {
            "code": code,
            "message": message,
        }
        if data is not None:
            self.json['data'] = data
        if page_num is not None:
            self.json['page'] = {
                "pageNum": page_num,
                "pageSize": page_size,
                "total": total,
            }
