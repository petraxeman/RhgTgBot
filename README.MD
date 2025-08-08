# Доступные комманды

## Команды администрирования


```/add_user $username```
```all:full adm:full adm:gr:users adm:add_user```
Добавляет пользователя с именем $username

```/del_user $username```
```all:full adm:full adm:gr:users adm:del_user```
Удаляет пользователя с именем $username

```/users_list```
```all:full adm:full adm:gr:users adm:users_list```
Возвращает список зарегистрированных пользователей.

```/app_args```
```all:full adm:full adm:gr:app adm:app_args```
Показывает список текущих настроек приложения.

```/set_app_arg $name $value```
```all:full adm:full adm:gr:app adm:set_app_arg```
Устанавливает настройку приложения приложения.

```/add_right $username $right```
```all:full adm:full adm:gr:rights adm:add_right```
Добавляет пользователю указанному в $username право $right.

```/sub_right $username $right```
```all:full adm:full adm:gr:rights adm:sub_right```
Удаляет у пользователя указанного в $username право $right.

```/show_rights```
```all:full adm:full adm:gr:rights adm:show_self_rights adm:show_rights```
Показывает ваши права. Эту функцию разрешает два права. ```adm:show_self_rights``` разрешает только эту фукнцию, а ```adm:show_rights``` так-же следующую.

```/show_rights $username```
```all:full adm:full adm:gr:rights adm:show_rights```
Показать права пользователя указанного в $username

## Команды Gemini

```/gmn_args```
```all:full gmn:full gmn:gr:settings gmn:gmn_args```
Показывает список текущих настроек текущего профиля Gemini, а так-же какой профиль сейчас используется.

```/set_gmn_arg $name $value```
```all:full gmn:full gmn:gr:settings gmn:set_gmn_arg```
Устанавливает настройку Gemini.

```/profiles```
```all:full gmn:full gmn:gr:profiles gmn:profiles```
Показывает список ваших текущих профилей.

```/clone_profile $name:opt```
```all:full gmn:full gmn:gr:profiles gmn:clone_profile```
Клонирует профиль. Если указано $name, то имя нового профиля будет $name, иначе оно будет именем текущего профиля + "_copy".

```/delete_profile $name```
```all:full gmn:full gmn:gr:profiles gmn:delete_profile```
Удаляет профиль.

```/rename_profile $old_name $new_name:opt```
```all:full gmn:full gmn:gr:profiles gmn:rename_profile```
Переименовывает профиль.
Если указано только $first_name то переименовывет текущий профиль на $first_name.
Если указано и $first_name и $second_name, то переименовывает профиль $first_name в профиль $second_name.

### Разговоры (gmn:gr:talking)

#### Любой текст в личном чате с ботом (gmn:private_ask)
Разрешает пользователю общаться с ботом в личном чате

#### Любой текст в группе при обращении к боту (gmn:ask)
Разрешает пользователю общаться в группе при обращении к боту.