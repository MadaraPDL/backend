from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.admin import Admin
from app.models.alert import Alert
from app.models.app_user import AppUser
from app.models.device import Device
from app.models.isp import ISP
from app.models.recommendation import Recommendation
from app.models.report import Report
from app.models.router import Router
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.models.subscription_plan import SubscriptionPlan
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription


DEMO_ISP_NAME = "PulseFi Demo ISP"
DEMO_ISP_EMAIL = "demo-isp@pulsefi-demo.com"

PLATFORM_ADMIN_EMAIL = "platform.demo@pulsefi-demo.com"
ISP_ADMIN_EMAIL = "isp.demo@pulsefi-demo.com"
APP_USER_EMAIL = "user.demo@pulsefi-demo.com"

PLATFORM_ADMIN_USERNAME = "platform_demo"
ISP_ADMIN_USERNAME = "isp_demo"
APP_USER_USERNAME = "user_demo"

DEMO_PASSWORD = "PulseFiDemo123!"


async def _scalar_one_or_none(db: AsyncSession, stmt):
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_or_create_isp(db: AsyncSession) -> ISP:
    isp = await _scalar_one_or_none(
        db,
        select(ISP).where(ISP.contact_email == DEMO_ISP_EMAIL),
    )

    if isp is not None:
        isp.name = DEMO_ISP_NAME
        isp.status = "active"
        return isp

    isp = ISP(
        name=DEMO_ISP_NAME,
        contact_email=DEMO_ISP_EMAIL,
        status="active",
    )
    db.add(isp)
    await db.flush()
    return isp


async def _get_or_create_admin(
    *,
    db: AsyncSession,
    email: str,
    username: str,
    full_name: str,
    role: str,
    isp_id,
) -> Admin:
    admin = await _scalar_one_or_none(
        db,
        select(Admin).where(Admin.email == email),
    )

    now = datetime.now(timezone.utc)

    if admin is None:
        admin = Admin(
            isp_id=isp_id,
            full_name=full_name,
            email=email,
            username=username,
            password_hash=hash_password(DEMO_PASSWORD),
            role=role,
            status="active",
            email_verified_at=now,
            password_changed_at=now,
            mfa_enabled=False,
            mfa_required=False,
            preferred_mfa_method="email",
        )
        db.add(admin)
        await db.flush()
        return admin

    admin.isp_id = isp_id
    admin.full_name = full_name
    admin.username = username
    admin.password_hash = hash_password(DEMO_PASSWORD)
    admin.role = role
    admin.status = "active"
    admin.email_verified_at = admin.email_verified_at or now
    admin.password_changed_at = now
    admin.mfa_enabled = False
    admin.mfa_required = False
    admin.preferred_mfa_method = "email"
    return admin


async def _get_or_create_app_user(
    *,
    db: AsyncSession,
    isp_id,
) -> AppUser:
    user = await _scalar_one_or_none(
        db,
        select(AppUser).where(AppUser.email == APP_USER_EMAIL),
    )

    now = datetime.now(timezone.utc)

    if user is None:
        user = AppUser(
            isp_id=isp_id,
            full_name="PulseFi Demo User",
            email=APP_USER_EMAIL,
            username=APP_USER_USERNAME,
            password_hash=hash_password(DEMO_PASSWORD),
            status="active",
            email_verified_at=now,
            password_changed_at=now,
            mfa_enabled=False,
            mfa_required=False,
            preferred_mfa_method="email",
        )
        db.add(user)
        await db.flush()
        return user

    user.isp_id = isp_id
    user.full_name = "PulseFi Demo User"
    user.username = APP_USER_USERNAME
    user.password_hash = hash_password(DEMO_PASSWORD)
    user.status = "active"
    user.email_verified_at = user.email_verified_at or now
    user.password_changed_at = now
    user.mfa_enabled = False
    user.mfa_required = False
    user.preferred_mfa_method = "email"
    return user


async def _get_or_create_plan(
    *,
    db: AsyncSession,
    isp_id,
    plan_name: str,
    monthly_price: Decimal,
    data_limit_gb: Decimal,
    speed_limit_mbps: Decimal,
    description: str,
    created_by_admin_id,
) -> SubscriptionPlan:
    plan = await _scalar_one_or_none(
        db,
        select(SubscriptionPlan).where(
            SubscriptionPlan.isp_id == isp_id,
            SubscriptionPlan.plan_name == plan_name,
        ),
    )

    if plan is None:
        plan = SubscriptionPlan(
            isp_id=isp_id,
            plan_name=plan_name,
            monthly_price=monthly_price,
            data_limit_gb=data_limit_gb,
            speed_limit_mbps=speed_limit_mbps,
            description=description,
            is_active=True,
            created_by_admin_id=created_by_admin_id,
        )
        db.add(plan)
        await db.flush()
        return plan

    plan.monthly_price = monthly_price
    plan.data_limit_gb = data_limit_gb
    plan.speed_limit_mbps = speed_limit_mbps
    plan.description = description
    plan.is_active = True
    plan.created_by_admin_id = created_by_admin_id
    return plan


async def _get_or_create_subscription(
    *,
    db: AsyncSession,
    user_id,
    plan_id,
    assigned_by_admin_id,
) -> UserSubscription:
    subscription = await _scalar_one_or_none(
        db,
        select(UserSubscription).where(
            UserSubscription.user_id == user_id,
            UserSubscription.subscription_label == "Demo Home Subscription",
        ),
    )

    if subscription is None:
        subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan_id,
            subscription_label="Demo Home Subscription",
            assigned_by_admin_id=assigned_by_admin_id,
            start_date=date.today(),
            end_date=None,
            status="active",
            auto_renew=True,
        )
        db.add(subscription)
        await db.flush()
        return subscription

    subscription.plan_id = plan_id
    subscription.assigned_by_admin_id = assigned_by_admin_id
    subscription.status = "active"
    subscription.auto_renew = True
    return subscription


async def _get_or_create_router(
    *,
    db: AsyncSession,
    isp_id,
    subscription_id,
    assigned_by_admin_id,
) -> Router:
    router = await _scalar_one_or_none(
        db,
        select(Router).where(
            Router.isp_id == isp_id,
            Router.mac_address == "AA:BB:CC:DD:EE:24",
        ),
    )

    if router is None:
        router = Router(
            isp_id=isp_id,
            user_subscription_id=subscription_id,
            assigned_by_admin_id=assigned_by_admin_id,
            router_name="Demo Home Router",
            router_model="PulseFi Simulator Router",
            router_ip="192.168.24.1",
            mac_address="AA:BB:CC:DD:EE:24",
            api_endpoint=None,
            username=None,
            password_encrypted=None,
            status="active",
        )
        db.add(router)
        await db.flush()
        return router

    router.user_subscription_id = subscription_id
    router.assigned_by_admin_id = assigned_by_admin_id
    router.router_name = "Demo Home Router"
    router.router_model = "PulseFi Simulator Router"
    router.router_ip = "192.168.24.1"
    router.status = "active"
    return router


async def _get_or_create_device(
    *,
    db: AsyncSession,
    router_id,
    user_id,
    device_name: str,
    mac_address: str,
    ip_address: str,
    device_type: str,
    is_trusted: bool,
    status: str,
) -> Device:
    device = await _scalar_one_or_none(
        db,
        select(Device).where(
            Device.router_id == router_id,
            Device.mac_address == mac_address,
        ),
    )

    now = datetime.now(timezone.utc)

    if device is None:
        device = Device(
            router_id=router_id,
            user_id=user_id,
            device_name=device_name,
            mac_address=mac_address,
            ip_address=ip_address,
            device_type=device_type,
            is_trusted=is_trusted,
            status=status,
            last_seen=now,
        )
        db.add(device)
        await db.flush()
        return device

    device.user_id = user_id
    device.device_name = device_name
    device.ip_address = ip_address
    device.device_type = device_type
    device.is_trusted = is_trusted
    device.status = status
    device.last_seen = now
    return device


async def _clear_generated_demo_records(
    *,
    db: AsyncSession,
    isp_id,
    user_id,
    subscription_id,
) -> None:
    await db.execute(
        delete(Report).where(
            Report.isp_id == isp_id,
            Report.title.like("Demo %"),
        )
    )
    await db.execute(
        delete(SubscriptionChangeRequest).where(
            SubscriptionChangeRequest.user_id == user_id,
            SubscriptionChangeRequest.reason.like("Demo %"),
        )
    )
    await db.execute(
        delete(Recommendation).where(
            Recommendation.user_id == user_id,
            Recommendation.reason.like("Demo %"),
        )
    )
    await db.execute(
        delete(Alert).where(
            Alert.user_id == user_id,
            Alert.title.like("Demo %"),
        )
    )
    await db.execute(
        delete(UsageRecord).where(
            UsageRecord.user_subscription_id == subscription_id,
            UsageRecord.source == "demo-seed",
        )
    )


async def seed_demo_data(*, apply: bool) -> None:
    if not settings.DEBUG:
        raise RuntimeError("Demo seed helper refuses to run when DEBUG=False.")

    async with AsyncSessionLocal() as db:
        isp = await _get_or_create_isp(db)
        await db.flush()

        platform_admin = await _get_or_create_admin(
            db=db,
            email=PLATFORM_ADMIN_EMAIL,
            username=PLATFORM_ADMIN_USERNAME,
            full_name="PulseFi Demo Platform Admin",
            role="platform_admin",
            isp_id=None,
        )
        await db.flush()

        isp.created_by_admin_id = platform_admin.id

        isp_admin = await _get_or_create_admin(
            db=db,
            email=ISP_ADMIN_EMAIL,
            username=ISP_ADMIN_USERNAME,
            full_name="PulseFi Demo ISP Admin",
            role="isp_admin",
            isp_id=isp.id,
        )
        await db.flush()

        app_user = await _get_or_create_app_user(
            db=db,
            isp_id=isp.id,
        )
        await db.flush()

        basic_plan = await _get_or_create_plan(
            db=db,
            isp_id=isp.id,
            plan_name="Demo Basic 100GB",
            monthly_price=Decimal("25.00"),
            data_limit_gb=Decimal("100"),
            speed_limit_mbps=Decimal("50"),
            description="Demo starter plan for presentation testing.",
            created_by_admin_id=isp_admin.id,
        )
        premium_plan = await _get_or_create_plan(
            db=db,
            isp_id=isp.id,
            plan_name="Demo Premium 250GB",
            monthly_price=Decimal("40.00"),
            data_limit_gb=Decimal("250"),
            speed_limit_mbps=Decimal("100"),
            description="Demo recommended upgrade plan for presentation testing.",
            created_by_admin_id=isp_admin.id,
        )
        await db.flush()

        subscription = await _get_or_create_subscription(
            db=db,
            user_id=app_user.id,
            plan_id=basic_plan.id,
            assigned_by_admin_id=isp_admin.id,
        )
        await db.flush()

        router = await _get_or_create_router(
            db=db,
            isp_id=isp.id,
            subscription_id=subscription.id,
            assigned_by_admin_id=isp_admin.id,
        )
        await db.flush()

        laptop = await _get_or_create_device(
            db=db,
            router_id=router.id,
            user_id=app_user.id,
            device_name="Demo Laptop",
            mac_address="AA:BB:CC:00:00:01",
            ip_address="192.168.24.20",
            device_type="laptop",
            is_trusted=True,
            status="connected",
        )
        phone = await _get_or_create_device(
            db=db,
            router_id=router.id,
            user_id=app_user.id,
            device_name="Demo Phone",
            mac_address="AA:BB:CC:00:00:02",
            ip_address="192.168.24.21",
            device_type="phone",
            is_trusted=True,
            status="connected",
        )
        unknown_device = await _get_or_create_device(
            db=db,
            router_id=router.id,
            user_id=app_user.id,
            device_name="Demo Unknown Device",
            mac_address="AA:BB:CC:00:00:03",
            ip_address="192.168.24.99",
            device_type="unknown",
            is_trusted=False,
            status="connected",
        )
        await db.flush()

        await _clear_generated_demo_records(
            db=db,
            isp_id=isp.id,
            user_id=app_user.id,
            subscription_id=subscription.id,
        )
        await db.flush()

        now = datetime.now(timezone.utc)

        usage_records = [
            UsageRecord(
                user_id=app_user.id,
                user_subscription_id=subscription.id,
                router_id=router.id,
                device_id=laptop.id,
                upload_mb=Decimal("450.00"),
                download_mb=Decimal("5600.00"),
                record_start=now - timedelta(days=2),
                record_end=now - timedelta(days=2, hours=-1),
                source="demo-seed",
            ),
            UsageRecord(
                user_id=app_user.id,
                user_subscription_id=subscription.id,
                router_id=router.id,
                device_id=phone.id,
                upload_mb=Decimal("250.00"),
                download_mb=Decimal("3200.00"),
                record_start=now - timedelta(days=1),
                record_end=now - timedelta(days=1, hours=-1),
                source="demo-seed",
            ),
            UsageRecord(
                user_id=app_user.id,
                user_subscription_id=subscription.id,
                router_id=router.id,
                device_id=unknown_device.id,
                upload_mb=Decimal("120.00"),
                download_mb=Decimal("950.00"),
                record_start=now - timedelta(hours=3),
                record_end=now - timedelta(hours=2),
                source="demo-seed",
            ),
        ]

        db.add_all(usage_records)

        alerts = [
            Alert(
                user_id=app_user.id,
                user_subscription_id=subscription.id,
                device_id=unknown_device.id,
                alert_type="new_device_connected",
                severity="critical",
                title="Demo New Device Detected",
                message="An unknown device joined the demo router network.",
                status="unread",
            ),
            Alert(
                user_id=app_user.id,
                user_subscription_id=subscription.id,
                device_id=None,
                alert_type="high_usage",
                severity="critical",
                title="Demo High Usage Warning",
                message="Demo usage is trending close to the current plan limit.",
                status="unread",
            ),
        ]

        recommendation = Recommendation(
            user_id=app_user.id,
            user_subscription_id=subscription.id,
            current_plan_id=basic_plan.id,
            recommendation_plan_id=premium_plan.id,
            prediction_id=None,
            recommendation_type="upgrade_plan",
            recommendation_text="Upgrade to Demo Premium 250GB to avoid exceeding your plan.",
            reason="Demo recommendation based on high usage trend.",
            confidence_score=Decimal("90.00"),
            status="new",
        )

        plan_change_request = SubscriptionChangeRequest(
            user_id=app_user.id,
            user_subscription_id=subscription.id,
            current_plan_id=basic_plan.id,
            requested_plan_id=premium_plan.id,
            recommendation_id=None,
            request_type="upgrade",
            reason="Demo pending upgrade request.",
            status="pending",
        )

        db.add_all(alerts + [recommendation, plan_change_request])

        if apply:
            await db.commit()
            print("Demo data seeded successfully.")
        else:
            await db.rollback()
            print("Dry run complete. No data was written.")

        print()
        print("Demo accounts:")
        print(f"Platform Admin: {PLATFORM_ADMIN_EMAIL} / {DEMO_PASSWORD}")
        print(f"ISP Admin:      {ISP_ADMIN_EMAIL} / {DEMO_PASSWORD}")
        print(f"App User:       {APP_USER_EMAIL} / {DEMO_PASSWORD}")
        print()
        print("Demo usernames:")
        print(f"Platform Admin: {PLATFORM_ADMIN_USERNAME}")
        print(f"ISP Admin:      {ISP_ADMIN_USERNAME}")
        print(f"App User:       {APP_USER_USERNAME}")
        print()
        print("Demo ISP:")
        print(f"{DEMO_ISP_NAME} ({DEMO_ISP_EMAIL})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed local PulseFi demo data. Refuses to run when DEBUG=False.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write demo data. Without this flag, the script performs a dry run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(seed_demo_data(apply=args.apply))


if __name__ == "__main__":
    main()

