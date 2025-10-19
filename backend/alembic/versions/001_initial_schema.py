"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-10-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('gender', sa.String(20)),
        sa.Column('height_cm', sa.Numeric(5, 2)),
        sa.Column('weight_kg', sa.Numeric(5, 2)),
        sa.Column('activity_level', sa.String(20)),
        sa.Column('goal_type', sa.String(20)),
        sa.Column('daily_calorie_target', sa.Integer()),
        sa.Column('protein_target_g', sa.Numeric(6, 2)),
        sa.Column('carbs_target_g', sa.Numeric(6, 2)),
        sa.Column('fats_target_g', sa.Numeric(6, 2)),
        sa.Column('water_target_ml', sa.Integer(), server_default='2000'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('email_verified', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('height_cm > 0', name='positive_height'),
        sa.CheckConstraint('weight_kg > 0', name='positive_weight'),
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Create foods table
    op.create_table(
        'foods',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('brand', sa.String(255)),
        sa.Column('barcode', sa.String(50)),
        sa.Column('source', sa.String(20), nullable=False),
        sa.Column('source_id', sa.String(100)),
        sa.Column('description', sa.Text()),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint("source IN ('openfoodfacts', 'usda', 'custom')", name='valid_source'),
    )
    op.create_index('idx_foods_name', 'foods', ['name'])
    op.create_index('idx_foods_barcode', 'foods', ['barcode'])
    op.create_index('idx_foods_source_id', 'foods', ['source', 'source_id'])

    # Create nutrition_info table
    op.create_table(
        'nutrition_info',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('food_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('serving_size', sa.Numeric(10, 2), nullable=False),
        sa.Column('serving_unit', sa.String(50), nullable=False),
        sa.Column('servings_per_container', sa.Numeric(6, 2)),
        sa.Column('calories', sa.Numeric(8, 2), nullable=False),
        sa.Column('protein_g', sa.Numeric(6, 2), server_default='0'),
        sa.Column('carbs_g', sa.Numeric(6, 2), server_default='0'),
        sa.Column('fats_g', sa.Numeric(6, 2), server_default='0'),
        sa.Column('fiber_g', sa.Numeric(6, 2)),
        sa.Column('sugar_g', sa.Numeric(6, 2)),
        sa.Column('saturated_fat_g', sa.Numeric(6, 2)),
        sa.Column('trans_fat_g', sa.Numeric(6, 2)),
        sa.Column('cholesterol_mg', sa.Numeric(6, 2)),
        sa.Column('sodium_mg', sa.Numeric(6, 2)),
        sa.Column('micronutrients', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['food_id'], ['foods.id'], ondelete='CASCADE'),
        sa.CheckConstraint('serving_size > 0', name='positive_serving'),
        sa.CheckConstraint('calories >= 0', name='positive_calories'),
        sa.CheckConstraint('protein_g >= 0 AND carbs_g >= 0 AND fats_g >= 0', name='positive_macros'),
    )
    op.create_index('idx_nutrition_food', 'nutrition_info', ['food_id'])

    # Create recipes table
    op.create_table(
        'recipes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('instructions', sa.Text()),
        sa.Column('prep_time_minutes', sa.Integer()),
        sa.Column('cook_time_minutes', sa.Integer()),
        sa.Column('servings', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_public', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('servings > 0', name='positive_servings'),
    )
    op.create_index('idx_recipes_user', 'recipes', ['user_id'])
    op.create_index('idx_recipes_name', 'recipes', ['name'])

    # Create recipe_ingredients table
    op.create_table(
        'recipe_ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('food_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['food_id'], ['foods.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('quantity > 0', name='positive_quantity'),
    )
    op.create_index('idx_recipe_ingredients_recipe', 'recipe_ingredients', ['recipe_id'])
    op.create_index('idx_recipe_ingredients_food', 'recipe_ingredients', ['food_id'])

    # Create meal_logs table
    op.create_table(
        'meal_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('food_id', postgresql.UUID(as_uuid=True)),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True)),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('calories', sa.Numeric(8, 2)),
        sa.Column('protein_g', sa.Numeric(6, 2)),
        sa.Column('carbs_g', sa.Numeric(6, 2)),
        sa.Column('fats_g', sa.Numeric(6, 2)),
        sa.Column('meal_type', sa.String(20), nullable=False),
        sa.Column('logged_date', sa.Date(), nullable=False),
        sa.Column('logged_time', sa.Time()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['food_id'], ['foods.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='SET NULL'),
        sa.CheckConstraint("meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')", name='valid_meal_type'),
        sa.CheckConstraint('quantity > 0', name='positive_quantity'),
    )
    op.create_index('idx_meal_logs_user_date', 'meal_logs', ['user_id', 'logged_date'])

    # Create favorites table
    op.create_table(
        'favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('food_id', postgresql.UUID(as_uuid=True)),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['food_id'], ['foods.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_favorites_user', 'favorites', ['user_id'])

    # Create water_logs table
    op.create_table(
        'water_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount_ml', sa.Integer(), nullable=False),
        sa.Column('logged_date', sa.Date(), nullable=False),
        sa.Column('logged_time', sa.Time()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('amount_ml > 0', name='positive_amount'),
    )
    op.create_index('idx_water_logs_user_date', 'water_logs', ['user_id', 'logged_date'])


def downgrade() -> None:
    op.drop_table('water_logs')
    op.drop_table('favorites')
    op.drop_table('meal_logs')
    op.drop_table('recipe_ingredients')
    op.drop_table('recipes')
    op.drop_table('nutrition_info')
    op.drop_table('foods')
    op.drop_table('users')
