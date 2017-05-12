def cache_styles(cls):

    _cache = {}

    def change_style_attributes(self, **attrs):
        _ts = self._replace(**attrs)
        ts = _cache.setdefault(hash(_ts), _ts)
        if ts is _ts:  # validate if we just added this new style to cache
            ts.validate(**attrs)
        return ts
    cls.set = change_style_attributes

    return cls
