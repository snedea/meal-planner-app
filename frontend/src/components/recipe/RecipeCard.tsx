// Recipe card component

import React from 'react';
import { Recipe } from '../../types/recipe.types';
import { Card } from '../common/Card';
import { Button } from '../common/Button';

interface RecipeCardProps {
  recipe: Recipe;
  onDelete?: (id: string) => void;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, onDelete }) => {
  return (
    <Card>
      <div className="space-y-3">
        <div>
          <h3 className="font-semibold text-lg text-gray-900">{recipe.name}</h3>
          {recipe.description && (
            <p className="text-sm text-gray-600 mt-1">{recipe.description}</p>
          )}
        </div>

        <div className="flex gap-4 text-sm text-gray-600">
          {recipe.prep_time_minutes && (
            <span>⏱️ Prep: {recipe.prep_time_minutes} min</span>
          )}
          {recipe.cook_time_minutes && (
            <span>🔥 Cook: {recipe.cook_time_minutes} min</span>
          )}
          <span>🍽️ {recipe.servings} servings</span>
        </div>

        {recipe.nutrition_per_serving && (
          <div className="grid grid-cols-4 gap-2 text-sm bg-gray-50 p-3 rounded">
            <div>
              <div className="text-gray-600">Calories</div>
              <div className="font-medium">{Math.round(recipe.nutrition_per_serving.calories)}</div>
            </div>
            <div>
              <div className="text-gray-600">Protein</div>
              <div className="font-medium">{Math.round(recipe.nutrition_per_serving.protein_g)}g</div>
            </div>
            <div>
              <div className="text-gray-600">Carbs</div>
              <div className="font-medium">{Math.round(recipe.nutrition_per_serving.carbs_g)}g</div>
            </div>
            <div>
              <div className="text-gray-600">Fats</div>
              <div className="font-medium">{Math.round(recipe.nutrition_per_serving.fats_g)}g</div>
            </div>
          </div>
        )}

        {onDelete && (
          <Button variant="danger" onClick={() => onDelete(recipe.id)} className="w-full text-sm">
            Delete Recipe
          </Button>
        )}
      </div>
    </Card>
  );
};
