-- USERS
INSERT INTO users (id, email, hashed_password, created_at, is_active) VALUES ('2b84b9e8-9ab4-4f97-b955-50e4b244c3a3', 'test@example.com', '$2b$12$jJHWvR18t8DPCmjKrQWgWuoJbSBOk3mIYNuhbcEuIrGZ1orPhPSJ6', '2025-07-15 16:59:38', True);
INSERT INTO users (id, email, hashed_password, created_at, is_active) VALUES ('d0127fa8-33de-485e-87d0-3b1149fc362a', 'test2@example.com', '$2b$12$sNZJjY154/d7zK0xwPk8iuyhm9ooFXDfdpgIbgIP4AffW9gPPbGwO', '2025-07-15 17:01:26', True);
INSERT INTO users (id, email, hashed_password, created_at, is_active) VALUES ('fdbc64ab-8564-4be6-87c2-998f0513fe52', 'onboarding@test.com', '$2b$12$iXczKEaIx6bPJ3J3yJwzpuY4kL5RiJCn0C/wapKzCFEFz4EaT4z6i', '2025-07-15 17:42:44', True);
INSERT INTO users (id, email, hashed_password, created_at, is_active) VALUES ('04e32e8c-5708-470f-b551-d9eda7daff0a', 'finaltest@example.com', '$2b$12$WGC5nJ01VdEtXzYfTfKhVudiVY7XJ4yyqbuEAynU0JzrTzVxrvO4i', '2025-07-15 17:55:28', True);

-- EXPENSE CATEGORIES
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (1, 'Food & Dining', 'Restaurants, groceries, coffee', NULL, 1, '2025-07-15 14:53:11');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (2, 'Transportation', 'Gas, Uber, public transit', NULL, 1, '2025-07-15 14:53:11');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (3, 'Entertainment', 'Movies, concerts, hobbies', NULL, 1, '2025-07-15 14:53:11');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (4, 'Shopping', 'Clothing, electronics, home goods', NULL, 1, '2025-07-15 14:53:11');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (5, 'Utilities', 'Electricity, water, internet', NULL, 1, '2025-07-15 14:53:11');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (6, 'Office Supplies', 'Office equipment and supplies', NULL, 1, '2025-07-15 17:51:38');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (7, 'Meals & Entertainment', 'Food, drinks, and entertainment', NULL, 1, '2025-07-15 17:51:38');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (8, 'Software & Subscriptions', 'Software licenses and subscriptions', NULL, 1, '2025-07-15 17:51:38');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (9, 'Marketing & Advertising', 'Marketing and advertising expenses', NULL, 1, '2025-07-15 17:51:38');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (10, 'Shipping & Postage', 'Shipping and postage costs', NULL, 1, '2025-07-15 17:51:38');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (11, 'Professional Development', 'Training and education', NULL, 1, '2025-07-15 17:51:38');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (12, 'Travel', 'Business travel expenses', NULL, 1, '2025-07-15 17:51:38');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (13, 'Insurance', 'Insurance premiums', NULL, 1, '2025-07-15 17:51:38');
INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES (14, 'Other', 'Miscellaneous expenses', NULL, 1, '2025-07-15 17:51:38');

-- EXPENSES

-- USER ACTIVITY

-- FEEDBACK
INSERT INTO feedback (id, user_id, category, message, rating, created_at) VALUES (1, 'fdbc64ab-8564-4be6-87c2-998f0513fe52', 'onboarding', 'The onboarding process was very smooth and intuitive. I love the checklist feature!', 5, '2025-07-15 17:43:11');
INSERT INTO feedback (id, user_id, category, message, rating, created_at) VALUES (2, '04e32e8c-5708-470f-b551-d9eda7daff0a', 'testing', 'Final system test feedback - everything working great!', 5, '2025-07-15 17:55:37');

-- PAYMENTS
