// Meal log page

import React, { useEffect } from 'react';
import { useMealLogStore } from '../store/mealLogStore';
import { useAuthStore } from '../store/authStore';
import { Card } from '../components/common/Card';
import { MealLogForm } from '../components/meal-log/MealLogForm';
import { MealLogList } from '../components/meal-log/MealLogList';
import { DailySummary } from '../components/meal-log/DailySummary';
import { format } from 'date-fns';

export const MealLog: React.FC = () => {
  const { user } = useAuthStore();
  const { dailySummary, currentDate, fetchLogs, setCurrentDate } = useMealLogStore();

  useEffect(() => {
    fetchLogs(currentDate);
  }, [currentDate, fetchLogs]);

  const defaultSummary = {
    total_calories: 0,
    total_protein_g: 0,
    total_carbs_g: 0,
    total_fats_g: 0,
    calorie_target: user?.daily_calorie_target || 2000,
    protein_target_g: user?.protein_target_g || 150,
    carbs_target_g: user?.carbs_target_g || 200,
    fats_target_g: user?.fats_target_g || 65,
    calorie_remaining: user?.daily_calorie_target || 2000,
    protein_remaining_g: user?.protein_target_g || 150,
    carbs_remaining_g: user?.carbs_target_g || 200,
    fats_remaining_g: user?.fats_target_g || 65,
  };

  const summary = dailySummary || defaultSummary;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Meal Log</h1>
          <p className="text-gray-600 mt-2">
            {format(new Date(currentDate), 'EEEE, MMMM d, yyyy')}
          </p>
        </div>

        <input
          type="date"
          value={currentDate}
          onChange={(e) => setCurrentDate(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card title="Log New Meal">
            <MealLogForm />
          </Card>

          <div>
            <h2 className="text-xl font-semibold mb-4">Today's Meals</h2>
            <MealLogList />
          </div>
        </div>

        <div>
          <DailySummary summary={summary} />
        </div>
      </div>
    </div>
  );
};
