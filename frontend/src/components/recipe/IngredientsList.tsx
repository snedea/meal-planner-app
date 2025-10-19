// Ingredients list component for recipes

import React from 'react';
import { RecipeIngredient } from '../../types/recipe.types';

interface IngredientsListProps {
  ingredients: RecipeIngredient[];
}

export const IngredientsList: React.FC<IngredientsListProps> = ({ ingredients }) => {
  if (!ingredients || ingredients.length === 0) {
    return <p className="text-gray-500">No ingredients listed</p>;
  }

  return (
    <ul className="space-y-2">
      {ingredients.map((ingredient, index) => (
        <li key={index} className="flex items-start">
          <span className="mr-2">•</span>
          <span>
            {ingredient.quantity} {ingredient.unit}{' '}
            {ingredient.food?.name || 'Unknown ingredient'}
          </span>
        </li>
      ))}
    </ul>
  );
};
