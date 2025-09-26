from rest_framework import serializers
from .models import Train, Certificates, Branding, JobCard, Crew, Override, InductionList

# InductionList Serializer
class InductionListSerializer(serializers.ModelSerializer):
    trainId = serializers.CharField(source='train.train_id')
    class Meta:
        model = InductionList
        fields = ['trainId', 'score', 'reason', 'override', 'violations']


# Certificates Serializer
class CertificatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificates
        fields = ['stock', 'signal', 'telecom']

    def to_representation(self, instance):
        def format_cert(dt):
            if not dt:
                return None
            # Output as 'YY/MM/DD HHMM' (military time)
            return dt.strftime('%y/%m/%d %H%M')

        return {
            'stock': format_cert(instance.stock),
            'signal': format_cert(instance.signal),
            'telecom': format_cert(instance.telecom),
        }

class BrandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branding
        fields = ['status', 'hours_remaining', 'total_hours']

class JobCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCard
        fields = ['title', 'priority']


# Crew Serializer
class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ['assigned', 'driver_id', 'valid_until']

# Override Serializer
class OverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Override
        fields = ['flag', 'category', 'reason', 'by']

# Custom field for jobCards
class JobCardsField(serializers.Field):
    def to_representation(self, obj):
        jobcards = JobCard.objects.filter(train=obj)
        return {
            'count': jobcards.count(),
            'all': JobCardSerializer(jobcards, many=True).data
        }

class TrainSerializer(serializers.ModelSerializer):
    certificates = CertificatesSerializer()
    branding = BrandingSerializer()
    jobCards = JobCardsField(source='*')
    mileage = serializers.SerializerMethodField()
    cleaningSlot = serializers.BooleanField(source='cleaning_slot')
    crew = CrewSerializer()
    override = OverrideSerializer()
    depotId = serializers.CharField(source='depot_id')

    class Meta:
        model = Train
        fields = [
            'train_id',
            'depotId',
            'certificates',
            'jobCards',
            'mileage',
            'branding',
            'cleaningSlot',
            'crew',
            'override',
        ]

    def get_mileage(self, obj):
        return {
            'odometer': obj.mileage_odometer,
            'lastService': obj.mileage_last_service.strftime('%Y-%m-%d') if obj.mileage_last_service else None
        }

