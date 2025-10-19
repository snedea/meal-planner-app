// Nutrition facts label component

import React from 'react';
import { NutritionInfo } from '../../types/food.types';

interface NutritionLabelProps {
  nutrition: NutritionInfo;
}

export const NutritionLabel: React.FC<NutritionLabelProps> = ({ nutrition }) => {
  return (
    <div className="border-2 border-black p-4 font-sans max-w-sm">
      <h3 className="font-bold text-2xl border-b-8 border-black pb-1">Nutrition Facts</h3>

      <div className="border-b-4 border-black py-1">
        <p className="text-sm">
          Serving Size: {nutrition.serving_size} {nutrition.serving_unit}
        </p>
      </div>

      <div className="border-b-4 border-black py-2">
        <div className="flex justify-between items-end">
          <span className="font-bold">Calories</span>
          <span className="font-bold text-2xl">{Math.round(nutrition.calories)}</span>
        </div>
      </div>

      <div className="border-b border-gray-400 py-2">
        <div className="flex justify-between">
          <span className="font-bold">Total Fat</span>
          <span>{Math.round(nutrition.fats_g)}g</span>
        </div>
        {nutrition.saturated_fat_g !== undefined && (
          <div className="flex justify-between ml-4 text-sm">
            <span>Saturated Fat</span>
            <span>{Math.round(nutrition.saturated_fat_g)}g</span>
          </div>
        )}
      </div>

      <div className="border-b border-gray-400 py-2">
        <div className="flex justify-between">
          <span className="font-bold">Carbohydrates</span>
          <span>{Math.round(nutrition.carbs_g)}g</span>
        </div>
        {nutrition.fiber_g !== undefined && (
          <div className="flex justify-between ml-4 text-sm">
            <span>Dietary Fiber</span>
            <span>{Math.round(nutrition.fiber_g)}g</span>
          </div>
        )}
        {nutrition.sugar_g !== undefined && (
          <div className="flex justify-between ml-4 text-sm">
            <span>Sugars</span>
            <span>{Math.round(nutrition.sugar_g)}g</span>
          </div>
        )}
      </div>

      <div className="border-b-4 border-black py-2">
        <div className="flex justify-between">
          <span className="font-bold">Protein</span>
          <span>{Math.round(nutrition.protein_g)}g</span>
        </div>
      </div>

      {nutrition.sodium_mg !== undefined && (
        <div className="py-2 text-sm">
          <div className="flex justify-between">
            <span>Sodium</span>
            <span>{Math.round(nutrition.sodium_mg)}mg</span>
          </div>
        </div>
      )}
    </div>
  );
};
