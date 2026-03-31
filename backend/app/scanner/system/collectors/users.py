import psutil

def collect_users():
    """
    Collect currently logged-in users
    """
    try:
        users = psutil.users()

        user_list = []
        for user in users:
            user_list.append({
                "name": user.name,
                "terminal": user.terminal,
                "host": user.host,
                "started": user.started
            })

        return user_list

    except Exception as e:
        return {"error": str(e)}