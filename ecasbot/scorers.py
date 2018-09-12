import re


class ScoreUserBase:
    MAGIC_PREFIX = 'score_'

    @classmethod
    def _get_handlers(cls):
        return {s for s in cls.__dict__.keys() if s.startswith(cls.MAGIC_PREFIX)}

    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger
        self._score_handlers = self._get_handlers()

    def score(self, username):
        s = 0
        for h in self._score_handlers:
            try:
                s += getattr(self, h)(username)
            except Exception as ex:
                self.logger.exception(ex)
        return s


class ScoreUser(ScoreUserBase):
    def score_chinese_0(self, username):
        # Find chinese bots and score them to +100...
        if re.search(self.settings.chkrgx, username, re.I | re.M | re.U):
            return 100

    @staticmethod
    def score_chinese_1(self, username):
        # Score users with chinese hieroglyphs...
        if re.search('[\u4e00-\u9fff]+', username, re.I | re.M | re.U):
            return 50

    def score_url_username(self, username):
        # Score users with URLs in username...
        if re.search(self.settings.urlrgx, username, re.I | re.M | re.U):
            return 100

    def score_stopwords_username(self, username):
        # Score users with restricted words in username...
        if any(w in username for w in self.settings.stopwords):
            return 100

    def score_long_username(self, username):
        # Score users with very long usernames...
        if len(username) > self.settings.maxname:
            return 50