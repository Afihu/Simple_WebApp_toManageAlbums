"""Lambda handler for /quota endpoint (task T036)."""
from ..services.quota_service import QuotaService
from . import utils

quota_service = QuotaService()


def get_quota(event, context):  # GET /quota
    user_id = utils.get_user_id(event)
    quota = quota_service.get_quota(user_id)
    return utils.ok(quota)
