from logging.handlers import SMTPHandler

DEV_TEAM_EMAILS_QUERY = '''SELECT DISTINCT email FROM
            members NATURAL JOIN current_position_holders NATURAL JOIN positions NATURAL JOIN groups 
            WHERE group_name = "Devteam" 
        '''


class DonutSMTPHandler(SMTPHandler):
    def __init__(self,
                 mailhost,
                 fromaddr,
                 toaddrs,
                 subject,
                 db_instance,
                 credentials=None,
                 secure=None,
                 timeout=5.0):
        super().__init__(mailhost, fromaddr, toaddrs, subject, credentials,
                         secure, timeout)
        self.db_instance = db_instance

    def emit(self, record):
        '''
        Overrides SMTPHandler's emit such that we dynamically
        get current donut dev team members
        '''
        self.toaddrs = self.getAdmins()
        super().emit(record)

    def getAdmins(self):
        ''' Returns current members in Devteam '''

        with self.db_instance.cursor() as cursor:
            cursor.execute(DEV_TEAM_EMAILS_QUERY, [])
            res = cursor.fetchall()
        return [result['email'] for result in res]
