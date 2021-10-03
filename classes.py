class User(object):
    def __init__(self, user_id):
        self.name = None
        self.user_id = user_id
        self.nickname = None

        self.reg_status = None
        self.stars = None

        self.dep_code = None
        self.dep_name = None
        self.dep_way = None

        self.arr_code = None
        self.arr_name = None
        self.arr_way = None

    def delete_account(self):
        self.name = None
        self.user_id = None
        self.nickname = None

        self.reg_status = False
        self.stars = None

        self.dep_code = None
        self.dep_name = None
        self.dep_way = None

        self.arr_code = None
        self.arr_name = None
        self.arr_way = None


class Confirmation(object):
    def __init__(self):
        self.user_id = None
        self.soul_id = None
        self.file_name = None
        self.date = None

    def reset(self):
        self.user_id = None
        self.soul_id = None
        self.file_name = None
        self.date = None


class Way(object):
    def __init__(self, ring_starts, ring_ends):
        # Less than this number are out of ring
        self.ring_starts_at = ring_starts

        # More than this number are out of ring
        self.ring_ends_at = ring_ends
