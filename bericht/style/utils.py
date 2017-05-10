def cache_styles(cls):

    _cache = {}

    def change_style_attributes(self, **attrs):
        _ts = self._replace(**attrs)
        ts = _cache.setdefault(hash(_ts), _ts)
        if ts is not _ts:  # skip validation on cached styles
            ts.validate(**attrs)
        return ts
    cls.set = change_style_attributes

    return cls
