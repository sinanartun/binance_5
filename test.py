import boto3


def get_current_region():
    session = boto3.session.Session()
    return session


if __name__ == '__main__':
    print(get_current_region())
