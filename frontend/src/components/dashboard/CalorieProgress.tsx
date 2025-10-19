// Calorie progress bar component

import React from 'react';
import { DailySummary } from '../../types/meal-log.types';

interface CalorieProgressProps {
  summary: DailySummary;
}

export const CalorieProgress: React.FC<CalorieProgressProps> = ({ summary }) => {
  const percentage = Math.min(
    (summary.total_calories / summary.calorie_target) * 100,
    100
  );

  const isOverTarget = summary.total_calories > summary.calorie_target;

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">Calories</span>
        <span className="text-sm text-gray-600">
          {Math.round(summary.total_calories)} / {summary.calorie_target} kcal
        </span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-4">
        <div
          className={`h-4 rounded-full transition-all ${
            isOverTarget ? 'bg-red-500' : 'bg-blue-600'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="text-right">
        <span
          className={`text-sm font-medium ${
            summary.calorie_remaining >= 0 ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {summary.calorie_remaining >= 0
            ? `${Math.round(summary.calorie_remaining)} remaining`
            : `${Math.abs(Math.round(summary.calorie_remaining))} over target`}
        </span>
      </div>
    </div>
  );
};
