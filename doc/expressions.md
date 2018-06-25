# Converting Expressions from Mistral -> Orchestra

## Jinja

* `_.xxx` becomes `ctx().xxx`

## YAQL

* `$.xxx` becomes `ctx().xxx` (how does this affect the `when` context for `$.` ?)

## Common

* `task('xxx').result` becomes `result()` , but only if the current task is `xxx`
* **TODO** How do we handle `task('yyy').result` when referencing a task outside of itself
* **TODO** How do we handle `st2kv.x.y.z` and `| decrypt_kv`
* **TODO** How do we handle other custom Jinja/YAQL filters https://docs.stackstorm.com/reference/jinja.html#custom-jinja-filters
* **TODO** Are custom filters going to be supported in the `| custom_filter` syntax, or just the `custom_filter()` syntax?
