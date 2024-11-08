from Components import CScoreMarker


class Entity:
    def __init__(self, id, tag):
        self.cTransform = None
        self.cShape = None
        self.cInput = None
        self.cGravity = None
        self.cTimer = None
        self.cAnimation = None
        self.cScoreMarker = CScoreMarker
        self._m_active= True
        self._m_id = id
        self._m_tag = tag

    def isActive(self):
        return self._m_active

    def tag(self):
        return self._m_tag

    def id(self):
        return self._m_id

    def destroy(self):
        self._m_active=False