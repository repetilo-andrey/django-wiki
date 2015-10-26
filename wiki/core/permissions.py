from __future__ import absolute_import
from __future__ import unicode_literals
from wiki.conf import settings

###############################
# ARTICLE PERMISSION HANDLING #
###############################
#
# All functions are:
#   can_something(article, user)
#      => True/False
#
# All functions can be replaced by pointing their relevant
# settings variable in wiki.conf.settings to a callable(article, user)


def can_read(article, user):
    if callable(settings.CAN_READ):
        return settings.CAN_READ(article, user)
    else:
        # Deny reading access to deleted articles if user has no delete access
        article_is_deleted = article.current_revision and article.current_revision.deleted
        if article_is_deleted and not article.can_delete(user):
            return False
        if user.is_anonymous():
            return False
        if user.has_wiki_access_read(user, article):
            return True
        return False


def can_write(article, user):
    if callable(settings.CAN_WRITE):
        return settings.CAN_WRITE(article, user)
    if user.is_anonymous():
        return False
    if user.has_wiki_access_read(user, article, 'write'):
        return True
    return False

def can_assign(article, user):
    if callable(settings.CAN_ASSIGN):
        return settings.CAN_ASSIGN(article, user)
    return not user.is_anonymous() and user.has_perm('wiki.assign')

def can_assign_owner(article, user):
    if callable(settings.CAN_ASSIGN_OWNER):
        return settings.CAN_ASSIGN_OWNER(article, user)
    return False

def can_change_permissions(article, user):
    if callable(settings.CAN_CHANGE_PERMISSIONS):
        return settings.CAN_CHANGE_PERMISSIONS(article, user)
    return (
        not user.is_anonymous() and (
            article.owner == user or 
            user.has_perm('wiki.assign')
        )
    )

def can_delete(article, user):
    if callable(settings.CAN_DELETE):
        return settings.CAN_DELETE(article, user)
    return not user.is_anonymous() and article.can_write(user)

def can_moderate(article, user):
    if callable(settings.CAN_MODERATE):
        return settings.CAN_MODERATE(article, user)
    return not user.is_anonymous() and user.has_perm('wiki.moderate')

def can_admin(article, user):
    if callable(settings.CAN_ADMIN):
        return settings.CAN_ADMIN(article, user)
    return not user.is_anonymous() and user.has_perm('wiki.admin')

