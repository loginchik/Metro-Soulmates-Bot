class User(object):
    def __init__(self, user_id):
        self.name = None
        self.user_id = user_id
        self.nickname = None

        self.reg_status = None

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

        self.dep_code = None
        self.dep_name = None
        self.dep_way = None

        self.arr_code = None
        self.arr_name = None
        self.arr_way = None