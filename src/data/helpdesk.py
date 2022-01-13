from re import fullmatch
import mongoengine as me

from .user import User


class Item(me.Document):
    full_name = me.StringField(required=True)
    alternative_names = me.ListField(field=me.StringField(), required=False)
    photo = me.StringField()
    description = me.StringField()
    initial_count = me.IntField(min_value=1)  # will not be changing
    count = me.IntField(min_value=0)
    max_per_team = me.IntField()

    # if reusable then it need to be returned
    is_reusable = me.BooleanField(default=False)

    @property
    def p_description(self) -> str:
        alternative_names = ", ".join(self.alternative_names)
        is_reusable = "Так" if self.is_reusable else "Ні"
        return (
            f"<b>{self.full_name}</b>\n\n"
            f"<b>Альтернативні назви</b> - {alternative_names}\n"
            f"<b>Опис</b> - {self.description}\n\n"
            f"<b>Початкова кількість</b> - {self.initial_count}\n"
            f"<b>Залишилось</b> - {self.count}\n"
            f"<b>Багаторазового використання</b> - {is_reusable}"
        )


class ItemLog(me.Document):
    item = me.ReferenceField(Item, required=True)
    user = me.ReferenceField(User, required=True)
    count = me.IntField(min_value=1, required=True)
    pick_up_datetime = me.DateTimeField(required=True)
    return_datetime = me.DateTimeField(required=False)


def init_data():

    items_list = list()

    items_list.append(
        Item(
            full_name="Молоток Vorel 30010 100 г",
            alternative_names=["Молоток", "Hammer"],
            photo="https://www.vigor-equipment.com/media/image/83/7d/48/v2665-detail-perspektiveMksy39TpAohwT.jpg",
            description="Молоток так молоток",
            initial_count=5,
            count=5,
            max_per_team=1,
            is_reusable=True,
        )
    )

    items_list.append(
        Item(
            full_name="Цвяхи будівельні 6x200 мм 1 кг без покриття",
            alternative_names=["Цвяхи", "nails"],
            photo="https://cdn.27.ua/499/35/13/144659_1.jpeg",
            description="Цвяхи класні",
            initial_count=50,
            count=50,
            max_per_team=10,
            is_reusable=False,
        )
    )

    items_list.append(
        Item(
            full_name="Дрель",
            alternative_names=["Дрель", "Drill"],
            photo="https://machtz.com.ua/files/resized/products/mid-13-1100-800x800-4.1200x1000w.jpg",
            description="Дрель чудова",
            initial_count=1,
            count=1,
            max_per_team=1,
            is_reusable=True,
        )
    )

    items_list.append(
        Item(
            full_name="Болт з шестигранною головкою DIN 933 М8×25 Детальніше: https://tk-ksk.com/ua/p38830705-bolt-shestigrannoj-golovkoj.html",
            alternative_names=["Болт", "Bolt"],
            photo="https://images.ua.prom.st/908190510_bolt-s-shestigrannoj.jpg",
            description="Болти класні",
            initial_count=50,
            count=50,
            max_per_team=5,
            is_reusable=False,
        )
    )

    items_list.append(
        Item(
            full_name="Клей Универсальный Контактный Момент 1 (30 Мл)",
            alternative_names=["Клей", "glue"],
            photo="https://intergips.ua/image/cache/catalog/items/products/prodakts%202017/klei%20kontaktnii/univers_Kley_Moment-1000x1000_0.jpg",
            description="Клей сильний",
            initial_count=2,
            count=2,
            max_per_team=1,
            is_reusable=True,
        )
    )

    for item in items_list:
        item.save()
