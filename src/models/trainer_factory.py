from src.models.base_trainer import Trainer, XGBoostTrainer, LGBMTrainer, CatTrainer

class TrainerFactory:
    _registry = {
        'xgboost': XGBoostTrainer,
        'lgbm': LGBMTrainer,
        'catboost': CatTrainer,
    }

    @classmethod
    def create_all(cls) -> list[Trainer]:
        return [trainer_cls() for trainer_cls in cls._registry.values()]