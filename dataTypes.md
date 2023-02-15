# New Data Types

| DataType name    | Python Data Type | Expected parameters                           |
|------------------|------------|-----------------------------------------------|
| channel_data     | Dictionary | {channel_id, owner_ids, member_ids, messages, is_public} |
| message_location | Dictionary | {message_id, channel_id}                      |
| user_global_permissions | Dictionary | {u_id, permission_id} |
| current_users | List | [{u_id, token}, ...] |
| password_data | Dictionary | {email, password} |
