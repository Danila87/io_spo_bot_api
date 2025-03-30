from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import ForeignKey, Column, String, Integer, Date, LargeBinary, inspect, DateTime, func


class Base(DeclarativeBase):
    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    dt_create = Column(DateTime, server_default=func.now())
    dt_update = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Songs(Base):

    __tablename__ = 'Songs'

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    title_search = Column(String, index=True)
    text = Column(String(5000))
    file_path = Column(String, nullable=True)
    category = Column(Integer, ForeignKey('CategorySong.id', ondelete='SET NULL'), nullable=True)

    rel_category = relationship('CategorySong', back_populates='rel_songs')


class CategorySong(Base):

    __tablename__ = 'CategorySong'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    parent_id = Column(Integer, nullable=True)

    rel_songs = relationship('Songs', back_populates='rel_category')


class Requests(Base):

    __tablename__ = 'Requests'

    id = Column(Integer, primary_key=True)

    id_user = Column(Integer, ForeignKey('TelegramUsers.id'), nullable=True)
    id_request_type = Column(Integer, ForeignKey('RequestTypes.id'))
    id_content = Column(Integer)

    content_display_value = Column(String(100))

    rel_user = relationship('TelegramUsers', back_populates='rel_requests')
    rel_request_type = relationship('RequestTypes', back_populates='rel_requests')


class RequestTypes(Base):

    __tablename__ = 'RequestTypes'

    id = Column(Integer, primary_key=True)
    title = Column(String(50))

    rel_requests = relationship('Requests', back_populates='rel_request_type')


class Users(Base):

    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)

    login = Column(String(50), unique=True)
    password = Column(LargeBinary)

    email = Column(String(150), nullable=True)


class TelegramUsers(Base):

    __tablename__ = 'TelegramUsers'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    nickname = Column(String)

    reviews = relationship('Reviews', back_populates='tg_users')
    rel_requests = relationship('Requests', back_populates='rel_user')

class SongBooks(Base):

    __tablename__ = 'SongBooks'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))
    file_path = Column(String(100))


class Reviews(Base):

    __tablename__ = 'Reviews'

    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('TelegramUsers.telegram_id'))

    text_review = Column(String(500))
    looked_status = Column(Integer)
    created_data = Column(Date)

    tg_users = relationship('TelegramUsers', back_populates='reviews')


class MethodicalBookChapters(Base):

    __tablename__ = 'MethodicalBookChapters'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, nullable=True)

    title = Column(String(200))
    file_path = Column(String(300), nullable=True)


class PiggyBankGroups(Base):

    """
    Чет я заебланил и обозвал по-странному. Таблица предназначена для хранения возрастов детей или групп
    """

    __tablename__ = 'PiggyBankGroups'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))

    rel_group_for_games = relationship('PiggyBankGroupForGame', back_populates='rel_groups')
    rel_group_for_legends = relationship('PiggyBankGroupsForLegend', back_populates='rel_groups')
    rel_group_for_ktd = relationship('PiggyBankGroupsForKTD', back_populates='rel_groups')


class PiggyBankTypesGame(Base):

    __tablename__ = 'PiggyBankTypesGame'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))

    rel_type_for_games = relationship('PiggyBankTypesGamesForGame', back_populates='rel_type_game')


class PiggyBankGames(Base):

    __tablename__ = 'PiggyBankGames'

    id = Column(Integer, primary_key=True)

    title = Column(String(100))
    description = Column(String(1024), nullable=True)
    file_path = Column(String(300), nullable=True)

    rel_groups_for_game = relationship('PiggyBankGroupForGame', back_populates='rel_games')
    rel_types_for_game = relationship('PiggyBankTypesGamesForGame', back_populates='rel_games')


class PiggyBankGroupForGame(Base):
    """
    Many to Many таблица для связи возраста и игры
    """

    __tablename__ = 'PiggyBankGroupForGame'

    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey('PiggyBankGroups.id'))
    game_id = Column(Integer, ForeignKey('PiggyBankGames.id'))

    rel_games = relationship('PiggyBankGames', back_populates='rel_groups_for_game')
    rel_groups = relationship('PiggyBankGroups', back_populates='rel_group_for_games')


class PiggyBankTypesGamesForGame(Base):

    """
    Many to Many таблица для связи типа игры и игры
    """

    __tablename__ = 'PiggyBankTypesGamesForGame'

    id = Column(Integer, primary_key=True)

    type_id = Column(Integer, ForeignKey('PiggyBankTypesGame.id'))
    game_id = Column(Integer, ForeignKey('PiggyBankGames.id'))

    rel_type_game = relationship('PiggyBankTypesGame', back_populates='rel_type_for_games')
    rel_games = relationship('PiggyBankGames', back_populates='rel_types_for_game')


class PiggyBankLegends(Base):

    __tablename__ = 'PiggyBankLegends'

    id = Column(Integer, primary_key=True)

    title = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)

    file_path = Column(String(1000), nullable=True)

    rel_groups = relationship('PiggyBankGroupsForLegend', back_populates='rel_legends')


class PiggyBankGroupsForLegend(Base):

    """
    Many to Many таблица для связи возраста и легенды
    """

    __tablename__ = 'PiggyBankGroupsForLegend'

    id = Column(Integer, primary_key=True)

    legend_id = Column(Integer, ForeignKey('PiggyBankLegends.id'))
    group_id = Column(Integer, ForeignKey('PiggyBankGroups.id'))

    rel_legends = relationship('PiggyBankLegends', back_populates='rel_groups')
    rel_groups = relationship('PiggyBankGroups', back_populates='rel_group_for_legends')


class PiggyBankKTD(Base):

    __tablename__ = 'PiggyBankKTD'

    id = Column(Integer, primary_key=True)

    title = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)

    file_path = Column(String(1000), nullable=True)

    rel_groups = relationship('PiggyBankGroupsForKTD', back_populates='rel_ktd')


class PiggyBankGroupsForKTD(Base):

    """
    Many to Many таблица для связи возраста и КТД
    """

    __tablename__ = 'PiggyBankGroupsForKTD'

    id = Column(Integer, primary_key=True)

    ktd_id = Column(Integer, ForeignKey('PiggyBankKTD.id'))
    group_id = Column(Integer, ForeignKey('PiggyBankGroups.id'))

    rel_ktd = relationship('PiggyBankKTD', back_populates='rel_groups')
    rel_groups = relationship('PiggyBankGroups', back_populates='rel_group_for_ktd')