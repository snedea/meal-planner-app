// Food card component

import React from 'react';
import { Food } from '../../types/food.types';
import { Card } from '../common/Card';
import { Button } from '../common/Button';

interface FoodCardProps {
  food: Food;
  onSelect?: (food: Food) => void;
}

export const FoodCard: React.FC<FoodCardProps> = ({ food, onSelect }) => {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <div className="space-y-3">
        <div>
          <h3 className="font-semibold text-lg text-gray-900">{food.name}</h3>
          {food.brand && <p className="text-sm text-gray-600">{food.brand}</p>}
          <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded mt-1">
            {food.source}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-gray-600">Serving:</span>
            <span className="ml-2 font-medium">
              {food.nutrition.serving_size} {food.nutrition.serving_unit}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Calories:</span>
            <span className="ml-2 font-medium">{Math.round(food.nutrition.calories)}</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 text-sm">
          <div>
            <div className="text-gray-600">Protein</div>
            <div className="font-medium">{Math.round(food.nutrition.protein_g)}g</div>
          </div>
          <div>
            <div className="text-gray-600">Carbs</div>
            <div className="font-medium">{Math.round(food.nutrition.carbs_g)}g</div>
          </div>
          <div>
            <div className="text-gray-600">Fats</div>
            <div className="font-medium">{Math.round(food.nutrition.fats_g)}g</div>
          </div>
        </div>

        {onSelect && (
          <Button variant="primary" onClick={() => onSelect(food)} className="w-full">
            Select Food
          </Button>
        )}
      </div>
    </Card>
  );
};
