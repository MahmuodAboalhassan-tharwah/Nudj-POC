from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.backend.app.framework.models import FrameworkDomainConfig
from src.backend.app.framework.schemas import FrameworkDomainConfigUpdate

# Default configurations to seed if missing
DEFAULT_DOMAINS = [
    {"domain_id": 1, "name_en": "HR Strategy", "name_ar": "استراتيجية الموارد البشرية", "default_weight": 1.0},
    {"domain_id": 2, "name_en": "Workforce Planning", "name_ar": "تخطيط القوى العاملة", "default_weight": 1.0},
    {"domain_id": 3, "name_en": "Talent Acquisition", "name_ar": "اكتساب المواهب", "default_weight": 1.0},
    {"domain_id": 4, "name_en": "Performance Management", "name_ar": "إدارة الأداء", "default_weight": 1.0},
    {"domain_id": 5, "name_en": "Learning & Development", "name_ar": "التعلم والتطوير", "default_weight": 1.0},
    {"domain_id": 6, "name_en": "Total Rewards", "name_ar": "المكافآت والتعويضات", "default_weight": 1.0},
    {"domain_id": 7, "name_en": "Employee Relations", "name_ar": "علاقات الموظفين", "default_weight": 1.0},
    {"domain_id": 8, "name_en": "HR Technology", "name_ar": "تقنية الموارد البشرية", "default_weight": 1.0},
    {"domain_id": 9, "name_en": "HR Analytics", "name_ar": "تحليلات الموارد البشرية", "default_weight": 1.0},
]

class FrameworkService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_configs(self) -> List[FrameworkDomainConfig]:
        query = select(FrameworkDomainConfig).order_by(FrameworkDomainConfig.domain_id)
        result = await self.db.execute(query)
        configs = result.scalars().all()
        
        if not configs:
            await self.seed_defaults()
            return await self.get_all_configs()
            
        return configs

    async def get_config_by_domain_id(self, domain_id: int) -> Optional[FrameworkDomainConfig]:
        query = select(FrameworkDomainConfig).where(FrameworkDomainConfig.domain_id == domain_id)
        result = await self.db.execute(query)
        return result.scalars().first()
        
    async def get_config(self, config_id: UUID) -> Optional[FrameworkDomainConfig]:
        return await self.db.get(FrameworkDomainConfig, config_id)

    async def update_config(self, domain_id: int, data: FrameworkDomainConfigUpdate) -> FrameworkDomainConfig:
        config = await self.get_config_by_domain_id(domain_id)
        if not config:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain config not found")
            
        if data.name_en is not None:
            config.name_en = data.name_en
        if data.name_ar is not None:
            config.name_ar = data.name_ar
        if data.description_en is not None:
            config.description_en = data.description_en
        if data.description_ar is not None:
            config.description_ar = data.description_ar
        if data.default_weight is not None:
            config.default_weight = data.default_weight
            
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def seed_defaults(self):
        # check if any exist to avoid duplicates if partial seed
        query = select(FrameworkDomainConfig)
        result = await self.db.execute(query)
        existing = result.scalars().all()
        existing_ids = {c.domain_id for c in existing}
        
        for domain in DEFAULT_DOMAINS:
            if domain["domain_id"] not in existing_ids:
                config = FrameworkDomainConfig(
                    domain_id=domain["domain_id"],
                    name_en=domain["name_en"],
                    name_ar=domain["name_ar"],
                    default_weight=domain["default_weight"]
                )
                self.db.add(config)
        
        await self.db.commit()
