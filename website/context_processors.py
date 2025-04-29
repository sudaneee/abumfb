from website.models import GeneralInformation, Carousel, Picture, Paragraph, Service, Staff, Blog, Feature




def data_processor(request):
    query = GeneralInformation.objects.all()[0]
    carousel = Carousel.objects.all().order_by('id')
    features = Feature.objects.all().order_by('id')
    md = Picture.objects.filter(title="md").first()
    cli = Picture.objects.filter(title="cli").first()
    services = Service.objects.all().order_by('id')
    staff = Staff.objects.all()
    vid = Picture.objects.get(title="vid")
    blogs = Blog.objects.all()
    footer = Picture.objects.get(title="footer")
    breadcumb = Picture.objects.get(title="breadcumb")



    return {
      'data': query,
      'carousels': carousel, 
      'features': features,
      'md': md,
      'cli': cli,
      'services': services,
      'staff': staff,
      'vid': vid,
      'blogs': blogs,
      'footer': footer,
      'breadcumb': breadcumb
    }