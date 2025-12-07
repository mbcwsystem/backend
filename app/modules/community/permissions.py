from app.utils.permission_utils import is_admin, is_staff, is_system

from .models import CategoryEnum


def can_write_post(user, category: CategoryEnum) -> bool:
    """
    게시글 작성 권한
    """
    # 출근용 계정 접근 불가
    if is_system(user):
        return False

    # 공지사항은 관리자만
    if category == CategoryEnum.notice:
        return is_admin(user)

    # 교대, 휴무는 자동생성
    if category in (CategoryEnum.shift, CategoryEnum.dayoff):
        return False

    # 자유게시판은 출근용 제외 모두
    if category == CategoryEnum.free_board:
        return is_admin(user) or is_staff(user)

    return False


def can_update_post(user, post_author_id: int) -> bool:
    """
    게시글 수정 권한
    """
    # 출근용 계정 접근 불가
    if is_system(user):
        return False

    # 작성자만
    return user.id == post_author_id


def can_delete_post(user, post_author_id: int, category: CategoryEnum) -> bool:
    """
    게시글 삭제 권한
    """
    # 출근용 계정 접근 불가
    if is_system(user):
        return False

    # 공지, 교대(대타), 휴무는 관리자만 삭제 가능
    if category in (CategoryEnum.notice, CategoryEnum.shift, CategoryEnum.dayoff):
        return is_admin(user)

    # 자유게시판은 관리자, 작성자
    if category == CategoryEnum.free_board:
        return is_admin(user) or (user.id == post_author_id)

    return False


def can_write_comment(user):
    """
    댓글 작성 권한
    """
    # 출근용 계정 제외 모두 가능
    return not is_system(user)


def can_update_comment(user, comment_author_id: int):
    """
    댓글 수정 권한
    """
    # 출근용 계정 접근 불가
    if is_system(user):
        return False

    # 댓글 작성자만
    return user.id == comment_author_id


def can_delete_comment(user, comment_author_id: int):
    """
    댓글 삭제 권한
    """
    # 출근용 계정 접근 불가
    if is_system(user):
        return False

    # 관리자도 댓글 삭제 가능
    if is_admin(user):
        return True

    # 댓글 작성자
    return user.id == comment_author_id
