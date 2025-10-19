// Dashboard page

import React, { useEffect } from 'react';
import { useMealLogStore } from '../store/mealLogStore';
import { useAuthStore } from '../store/authStore';
import { Card } from '../components/common/Card';
import { Spinner } from '../components/common/Spinner';
import { CalorieProgress } from '../components/dashboard/CalorieProgress';
import { MacroBreakdown } from '../components/dashboard/MacroBreakdown';
import { QuickActions } from '../components/dashboard/QuickActions';
import { format } from 'date-fns';

export const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const { dailySummary, currentDate, fetchLogs, isLoading } = useMealLogStore();

  useEffect(() => {
    fetchLogs(currentDate);
  }, [currentDate, fetchLogs]);

  if (isLoading && !dailySummary) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

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
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.first_name || user?.email}!
        </h1>
        <p className="text-gray-600 mt-2">
          {format(new Date(currentDate), 'EEEE, MMMM d, yyyy')}
        </p>
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Calorie Progress Card */}
        <Card title="Daily Calorie Goal">
          <CalorieProgress summary={summary} />
        </Card>

        {/* Macro Breakdown Card */}
        <Card title="Macronutrient Breakdown">
          <MacroBreakdown summary={summary} />
        </Card>
      </div>

      {/* Today's Summary Stats */}
      <Card title="Today's Summary">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {Math.round(summary.total_calories)}
            </div>
            <div className="text-sm text-gray-600">Calories</div>
          </div>

          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {Math.round(summary.total_protein_g)}g
            </div>
            <div className="text-sm text-gray-600">Protein</div>
          </div>

          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              {Math.round(summary.total_carbs_g)}g
            </div>
            <div className="text-sm text-gray-600">Carbs</div>
          </div>

          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {Math.round(summary.total_fats_g)}g
            </div>
            <div className="text-sm text-gray-600">Fats</div>
          </div>
        </div>
      </Card>
    </div>
  );
};
