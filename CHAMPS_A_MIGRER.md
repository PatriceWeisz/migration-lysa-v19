# CHAMPS À MIGRER PAR MODULE

## account.tax (20 champs)
```python
CHAMPS = [
    'name', 'amount', 'amount_type', 'type_tax_use',
    'description', 'price_include', 'include_base_amount',
    'analytic', 'tax_exigibility', 'cash_basis_transition_account_id',
    'tax_group_id', 'tax_scope', 'sequence',
    'children_tax_ids', 'invoice_repartition_line_ids',
    'refund_repartition_line_ids', 'is_base_affected',
    'company_id', 'country_id', 'active'
]
```

## product.pricelist (7 champs)
```python
CHAMPS = [
    'name', 'currency_id', 'company_id', 'active',
    'item_ids', 'sequence', 'country_group_ids'
]
```

## crm.team (13 champs)
```python
CHAMPS = [
    'name', 'user_id', 'company_id', 'active',
    'color', 'sequence', 'invoiced_target',
    'member_ids', 'crm_team_member_ids', 'crm_team_member_all_ids',
    'favorite_user_ids', 'is_favorite', 'message_partner_ids'
]
```

## project.project (44 champs)
```python
CHAMPS = [
    'name', 'user_id', 'partner_id', 'company_id', 'active',
    'access_token', 'activity_summary', 'activity_type_id', 'activity_user_id',
    'alias_id', 'alias_name', 'alias_contact', 'alias_defaults',
    'alias_model_id', 'alias_parent_model_id', 'alias_parent_thread_id',
    'alias_force_thread_id', 'alias_bounced_content',
    'allow_billable', 'allow_milestones', 'allow_recurring_tasks',
    'allow_task_dependencies', 'collaborator_ids', 'color',
    'date', 'date_start', 'description', 'email', 'favorite_user_ids',
    'is_favorite', 'label_tasks', 'message_partner_ids',
    'partner_email', 'partner_phone', 'phone', 'privacy_visibility',
    'rating_percentage_satisfaction', 'rating_status',
    'resource_calendar_id', 'sequence', 'tag_ids', 'task_ids',
    'task_properties_definition', 'type_ids', 'user_ids'
]
```

## account.analytic.account (13 champs)
```python
CHAMPS = [
    'name', 'code', 'partner_id', 'company_id', 'active',
    'plan_id', 'root_plan_id', 'line_ids', 'message_partner_ids',
    'bom_ids', 'production_ids', 'project_ids', 'workcenter_ids'
]
```

## res.partner.category (7 champs)
```python
CHAMPS = [
    'name', 'color', 'parent_id', 'active',
    'child_ids', 'parent_path', 'partner_ids'
]
```

## res.users (121 champs - TOP 30 prioritaires)
```python
CHAMPS = [
    'name', 'login', 'email', 'active', 'partner_id', 'company_id',
    'groups_id', 'lang', 'tz', 'signature', 'notification_type',
    'odoobot_state', 'phone', 'mobile', 'city', 'street',
    'street2', 'zip', 'country_id', 'state_id',
    'category_id', 'comment', 'image_1920', 'website',
    'function', 'title', 'sel_groups_1_9_10', 'share',
    'action_id', 'employee_ids', 'resource_ids'
]
```

---

**NOTE:** Certains champs sont des relations (one2many) qui nécessitent un traitement spécial.

