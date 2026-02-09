import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from src.backend.app.framework.service import FrameworkService
from src.backend.app.framework.models import FrameworkDomainConfig
from src.backend.app.framework.schemas import FrameworkDomainConfigUpdate

@pytest.mark.asyncio
async def test_seed_defaults_creates_configs():
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = FrameworkService(mock_db)
    
    # Mock empty existing configs
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    # Act
    await service.seed_defaults()

    # Assert
    # Should have added 9 domains
    assert mock_db.add.call_count == 9
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_update_config_updates_weight():
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = FrameworkService(mock_db)
    
    domain_id = 1
    new_weight = 2.5
    
    # Mock existing config
    existing_config = FrameworkDomainConfig(
        id=uuid4(),
        domain_id=domain_id,
        name_en="Test Domain",
        name_ar="Test Domain AR",
        default_weight=1.0
    )
    
    # Mock get_config_by_domain_id query execution
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = existing_config
    mock_db.execute.return_value = mock_result
    
    update_data = FrameworkDomainConfigUpdate(default_weight=new_weight)

    # Act
    updated_config = await service.update_config(domain_id, update_data)

    # Assert
    assert updated_config.default_weight == new_weight
    assert mock_db.commit.called
    assert mock_db.refresh.called
