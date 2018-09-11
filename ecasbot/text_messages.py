class FmtMsg:
    def __init__(self, text, extractor=None):
        self.__t = text
        self.__e = extractor

    def __call__(self, *args, **kwargs):
        fmt_args, fmt_kwargs = args, kwargs
        if self.__e:
            fmt_args, fmt_kwargs = self.__e(args, kwargs)
        return self.__t.format(*fmt_args, **fmt_kwargs)


class Transformers:
    Alog = lambda args, kwargs: (
        (
            args[0].new_chat_member.first_name,
            args[0].new_chat_member.id,
            args[1]
            ),
        {}
        )

    Amsgrm = lambda args, kwargs: (
        (
            args[0].from_user.first_name,
            args[0].from_user.id,
            args[0].reply_to_message.from_user.first_name,
            args[0].reply_to_message.from_user.id
            ),
        {}
        )

    MuteBan = lambda args, kwargs: (
        (
            args[0].from_user.first_name,
            args[0].from_user.id,
            args[1].username,
            args[1].userid
            ),
        {}
        )
    Aunres = lambda args, kwargs: (
        (
            args[0].from_user.first_name,
            args[0].from_user.id,
            args[0].reply_to_message.from_user.first_name,
            args[0].reply_to_message.from_user.id
            ),
        {}
        )


class Messages:
    Welcome = FmtMsg('Add me to supergroup and give me admin rights. I will try to block spammers automatically.')
    Alog = FmtMsg(
        'New user {} with ID {} has joined group. Score: {}.',
        Transformers.Alog
        )
    Restex = FmtMsg('Cannot restrict a new user with ID {} due to missing admin rights.')
    Msgex = FmtMsg('Exception detected while handling spam message from {}.')
    Notoken = FmtMsg('No API token entered. Cannot proceed. Fix this issue and run this bot again!')
    Joinhex = FmtMsg('Failed to handle join message.')
    Banned = FmtMsg('Permanently banned user with ID {} (score: {}).')
    Msgrest = FmtMsg(
        'Removed message from restricted user {} with ID {}.',
        lambda args, kwargs: (
            (
                args[0].from_user.first_name,
                args[0].from_user.id
                ),
            {}
            )
        )

    Amsgrm = FmtMsg(
        'Admin {} ({}) removed message from user {} with ID {}.',
        Transformers.Amsgrm
        )
    Amute = FmtMsg(
        'Admin {} ({}) permanently muted user {} with ID {}.',
        Transformers.MuteBan
        )
    Aunres = FmtMsg(
        'Admin {} ({}) removed all restrictions from user {} with ID {}.',
        Transformers.Aunres
        )
    Aban = FmtMsg(
        'Admin {} ({}) permanently banned user {} with ID {}.',
        Transformers.MuteBan
        )
    Admerr = FmtMsg('Failed to handle admin command.')
    Chkme = FmtMsg('Checking of account {} successfully completed. Your score is: {}.')
    Pmex = FmtMsg('Failed to handle command in private chat with bot.')