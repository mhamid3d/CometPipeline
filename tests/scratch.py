import mongorm
import datetime

db = mongorm.getHandler()

obj = db['version'].get("9cb22e87-62b7-4c78-ada0-b528eba1da97")

mod = obj.modified
print mod.strftime("%b %d %Y %I:%M %p")