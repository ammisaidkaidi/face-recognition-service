class IdentitySmoother:
    def __init__(self, stable_frames:int, unknown_frames:int):
        self.stable_frames=stable_frames; self.unknown_frames=unknown_frames; self.current=None; self.candidate=None; self.count=0
    def update(self, identity: str|None) -> str|None:
        if identity == self.current: self.candidate=None; self.count=0; return self.current
        if identity != self.candidate: self.candidate=identity; self.count=1
        else: self.count+=1
        needed=self.unknown_frames if identity is None else self.stable_frames
        if self.count>=needed: self.current=identity; self.candidate=None; self.count=0
        return self.current
