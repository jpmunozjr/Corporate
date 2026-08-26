class GroupMeAlerter(Alerter):
    """ Sends an email alert """
    required_options = frozenset(['bot_id'])

    def __init__(self, *args):
        super(GroupMeAlerter, self).__init__(*args)

    def alert(self, matches):
		api_url = "https://api.groupme.com/v3/bots/post"
		to_addr = self.rule['bot_id']
		
		subject = self.create_title(matches)
		body = self.create_alert_body(matches)
		
		data = urllib.urlencode({"bot_id": self.rule['bot_id'], "text": ASDF})
		post = urllib2.urlopen(url=api_url, data=data)

        elastalert_logger.info("Sent message to GroupMe, bot ID: %s" % (to_addr))

    def create_default_title(self, matches):
        subject = 'ElastAlert: %s \n\n' % (self.rule['name'])

        # If the rule has a query_key, add that value plus timestamp to subject
        if 'query_key' in self.rule:
            qk = matches[0].get(self.rule['query_key'])
            if qk:
                subject += ' - %s' % (qk)

        return subject

    def get_info(self):
        return {'type': 'groupme',
                'recipients': self.rule['bot_id']}