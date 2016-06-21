import whoosh

from flask.ext.whooshee import AbstractWhoosheer

from coprs import models
from coprs import whooshee
from coprs import db

@whooshee.register_whoosheer
class CoprWhoosheer(AbstractWhoosheer):
    schema = whoosh.fields.Schema(
        copr_id=whoosh.fields.NUMERIC(stored=True, unique=True),
        user_id=whoosh.fields.NUMERIC(stored=True),
        group_id=whoosh.fields.NUMERIC(stored=True),
        # treat dash as a normal character - so searching for example
        # "copr-dev" will really search for "copr-dev"
        ownername=whoosh.fields.TEXT(
            analyzer=whoosh.analysis.StandardAnalyzer(
                expression=r"@?\w+(-\.?\w+)*"), field_boost=2),
        coprname=whoosh.fields.TEXT(
            analyzer=whoosh.analysis.StandardAnalyzer(
                expression=r"\w+(-\.?\w+)*"), field_boost=3),
        chroots=whoosh.fields.TEXT(field_boost=2),
        packages=whoosh.fields.TEXT(
            analyzer=whoosh.analysis.StandardAnalyzer(
                expression=r"\s+", gaps=True), field_boost=2),
        description=whoosh.fields.TEXT(),
        instructions=whoosh.fields.TEXT())

    models = [models.Copr, models.User, models.Group, models.Package]

    @classmethod
    def update_copr(cls, writer, copr):
        writer.update_document(copr_id=copr.id,
                               user_id=copr.user.id,
                               group_id=copr.group.id if copr.group else None,
                               ownername=copr.owner_name,
                               coprname=copr.name,
                               chroots=cls.get_chroot_info(copr),
                               packages=cls.get_package_names(copr),
                               description=copr.description,
                               instructions=copr.instructions)

    @classmethod
    def update_package(cls, writer, package):
        writer.update_document(copr_id=package.copr.id, packages=cls.get_package_names(package.copr))

    @classmethod
    def insert_copr(cls, writer, copr):
        writer.add_document(copr_id=copr.id,
                            user_id=copr.user.id,
                            group_id=copr.group.id if copr.group else None,
                            ownername=copr.owner_name,
                            coprname=copr.name,
                            chroots=cls.get_chroot_info(copr),
                            packages=cls.get_package_names(copr),
                            description=copr.description,
                            instructions=copr.instructions)

    @classmethod
    def insert_package(cls, writer, package):
        writer.update_document(copr_id=package.copr.id, packages=cls.get_package_names(package.copr))

    @classmethod
    def delete_copr(cls, writer, copr):
        writer.delete_by_term("copr_id", copr.id)

    @classmethod
    def delete_package(cls, writer, package):
        writer.update_document(copr_id=package.copr.id, packages=cls.get_package_names(package.copr))

    @classmethod
    def get_chroot_info(cls, copr):
        # NOTE: orm db session for Copr model is already commited at the point insert_*/update_* methods are called.
        # Hence we use db.engine directly (for a new session).
        result = db.engine.execute(
            """
            SELECT os_release, os_version, arch
            FROM mock_chroot
            JOIN copr_chroot ON copr_chroot.mock_chroot_id=mock_chroot.id
            WHERE copr_chroot.copr_id={0}
            """.format(copr.id)
        )
        return ["{}-{}-{}".format(t[0], t[1], t[2]) for t in result.fetchall()]

    @classmethod
    def get_package_names(cls, copr):
        result = db.engine.execute(
            """
            SELECT name
            FROM package
            WHERE copr_id={0}
            """.format(copr.id)
        )
        return [row[0] for row in result.fetchall()]
