class Corpus:

    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.lemmas = []
        self.pos_tags = []
        self.syn_deps = []
        self.is_stops = []
        self.named_entities = []

    def store_preprocess_pipeline(self, tokens, lemmas, pos_tags, syn_deps, is_stops, named_entities):
        self.tokens = tokens
        self.lemmas = lemmas
        self.pos_tags = pos_tags
        self.syn_deps = syn_deps
        self.is_stops = is_stops
        self.named_entities = named_entities
