const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: 'ap-south-1_sXfyJ5izx',      // e.g., ap-south-1_xxxxxxxxx
      userPoolClientId: '6kkda5bp2nbn1rf8hi4dekbeoe',    // e.g., 1a2b3c4d5e6f7g8h9i0j1k2l3m
      loginWith: {
        email: true,
      },
    }
  }
};

export default awsConfig;
