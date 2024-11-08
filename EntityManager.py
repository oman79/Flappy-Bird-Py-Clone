from typing import List
from Entity import Entity

class EntityManager:
    def __init__(self):
        self._m_entities = []
        self._m_entitiesToAdd = []
        self._m_entityMap = {}
        self._m_totalEntities = 0

    def update(self):
        for e in self._m_entitiesToAdd:
            e: Entity
            self._m_entities.append(e)
            self._m_entityMap.setdefault(e._m_tag , [])
            self._m_entityMap[e._m_tag].append(e)
        self._m_entitiesToAdd.clear()

        self._removeDeadEntities(self._m_entities)
        for entityVec in self._m_entityMap.values():
            self._removeDeadEntities(entityVec)

    def _removeDeadEntities(self, entity_vec: list):
        entity_vec: List[Entity]
        for i in reversed(range(len(entity_vec))):
            if not entity_vec[i].isActive():
                entity_vec.pop(i)

    def addEntity(self, tag: str):
        self._m_totalEntities+=1
        entity = Entity(self._m_totalEntities, tag)
        self._m_entitiesToAdd.append(entity)
        return entity

    def getEntities(self, tag = "no_tag"):
        if tag== "no_tag":
            return self._m_entities
        else:
            return self._m_entityMap.get(tag, [])