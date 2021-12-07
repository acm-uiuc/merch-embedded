import sqlite3

def open_db():
  con = sqlite3.connect('inventory.sqlite')
  cur = con.cursor()
  return (con, cur)

def close_db(con):
  con.commit()
  con.close()

def db_action(action):
  def wrapped_action(*args, **kwargs):
    con, cur = open_db()
    result = action(*args, cur, **kwargs)
    close_db(con)
    return result
  return wrapped_action

def enforce_required(arg_dict, *args):
  for arg in args:
    if arg_dict.get(arg) is None:
      return (False, f'argument {arg} is required but not present')
  return (True, "")

def enforce_natural_number(arg_dict, *args):
  for arg in args:
    arg_val = arg_dict.get(arg)
    if arg_val is not None:
      if not arg_val.isdigit():
        return (False, f'argument {arg} should be a natural number')
  return (True, "")

def arg_dict_ensure_keys(arg_dict, keys):
  for key in keys:
    if key not in arg_dict:
      arg_dict[key] = None
  return arg_dict

@db_action
def init_db(cur):
  cur.execute('''CREATE TABLE IF NOT EXISTS items (
                   name TEXT NOT NULL UNIQUE,
                   image_url TEXT NOT NULL,
                   price INTEGER NOT NULL,
                   calories INTEGER,
                   fat INTEGER,
                   carbs INTEGER,
                   fiber INTEGER,
                   sugar INTEGER,
                   protein INTEGER
                 )''')
  cur.execute('''CREATE TABLE IF NOT EXISTS locations (
                   location TEXT NOT NULL UNIQUE,
                   item INTEGER NOT NULL,
                   quantity INTEGER NOT NULL,
                   FOREIGN KEY(item) REFERENCES items(rowid)
                 )''')

@db_action
def insert_item(request_args, cur):
  '''Adds an item to the items table.

  Args:
    name: The name of the item to add. Required. Must be unique.
    image_url: The image url of the item to add. Required.
    price: The price in USD cents of the item to add. Integer. Required.
    calories: The number of calories in the item. Integer.
    fat: Grams of fat in the item. Integer.
    carbs: Grams of carbs in the item. Integer.
    fiber: Grams of fiber in the item. Integer.
    sugar: Grams of sugar in the item. Integer.
    protein: Grams of protein in the item. Integer.
  '''
  arg_dict = request_args.to_dict()
  res = enforce_required(arg_dict, 'name', 'image_url', 'price')
  if not res[0]:
    return res
  res = enforce_natural_number(arg_dict, 'price', 'calories', 'fat', 'carbs',
                               'fiber', 'sugar', 'protein')
  if not res[0]:
    return res
  arg_dict = arg_dict_ensure_keys(arg_dict, ['name', 'image_url', 'price',
                                             'calories', 'fat', 'carbs',
                                             'fiber', 'sugar', 'protein'])
  try:
    cur.execute('''INSERT INTO items VALUES (:name, :image_url, :price,
                                             :calories, :fat, :carbs, :fiber,
                                             :sugar, :protein)''', arg_dict)
  except sqlite3.DatabaseError as e:
    if "UNIQUE" in str(e):
      return (False, 'this item is already in the inventory')
    return (False, "")
  return (True, "")

@db_action
def select_items(cur):
  '''Returns a list of items.
  '''
  cur.execute('''SELECT b.rowid, b.name, b.image_url, b.price, b.calories,
                        b.fat, b.carbs, b.fiber, b.sugar, b.protein,
                        IFNULL(SUM(t.quantity), 0),
                        GROUP_CONCAT(t.location, ", ")
                 FROM items b
                 LEFT JOIN locations t ON t.item = b.rowid
                 GROUP BY b.rowid, b.name, b.image_url, b.price, b.calories,
                          b.fat, b.carbs, b.fiber, b.sugar, b.protein''')
  items = cur.fetchall()
  dict_items = []
  column_names = ['rowid', 'name', 'image_url', 'price', 'calories', 'fat',
                  'carbs', 'fiber', 'sugar', 'protein', 'quantity', 'locations']
  for item in items:
    item_dict = {}
    for i in range(0, len(column_names)):
      if item[i] is not None:
        item_dict[column_names[i]] = item[i]
    if 'locations' in item_dict:
      item_dict['locations'] = item[i].split(', ')
    dict_items.append(item_dict)
  return dict_items
