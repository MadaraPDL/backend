from pydantic import BaseModel


class StatusCounts(BaseModel):
    total: int = 0
    active: int = 0
    inactive: int = 0
    suspended: int = 0
    pending: int = 0
    expired: int = 0
    cancelled: int = 0
    maintenance: int = 0


class ISPAdminSummaryResponse(BaseModel):
    isp_id: str
    users: StatusCounts
    plans: StatusCounts
    subscriptions: StatusCounts
    routers: StatusCounts