#include <stdlib.h>
#include <stdio.h>
#include <math.h>


void particlePositions(int Np, int Ne, float* X, float* Y, int* cells, float* LC, float* BC, float dt, float density, float c, float Tt, float E, float Nu, float sigf, float* Positions){

    float Xr[Np];
    float Yr[Np];
    
    int C1[Ne][3];
    int i = 0;

    while(i < Np){
        Xr[i] = X[i];
        Yr[i] = Y[i];

        i++;
    }
    i = 0;
    
    while(i < Ne){
        C1[i][0] = cells[3*i];
        C1[i][1] = cells[3*i + 1];
        C1[i][2] = cells[3*i + 2];
        i++;
    }

    int Nem = 0;

    float SED;
    float SEDmin = sigf*sigf/(2*E);
    float XD,YD,XR,YR,XDh,YDh,XDv,YDv,XRh,YRh,XRv,YRv;
    float P,Q,R,S,T,U,V,W;
    float EXX,EYY,EXY,ZXX,ZYY,ZXY;
    float EXX_X,EXX_Y,EYY_X,EYY_Y,EXY_X,EXY_Y;
    float ZXX_X,ZXX_Y,ZYY_X,ZYY_Y,ZXY_X,ZXY_Y;

    float Q0[Np];
    float Q1[Np];
    float Q2[Np];

    float Fx[Np];
    float Fy[Np];
    float Nse[Np];

    int temp;
    float Area;
    int Nt=Tt/dt;
    int N;
    float G=E/2*(Nu+1);

    for (int i=0;i<Np;i++){

        Nse[i]=0;
        Fx[i]=0;
        Fy[i]=0;

    }

    // Calculate the maximum shared elements per node
    //C1 - Points of elements

    for (int i=0;i<Np;i++){

        for (int j=0;j<Ne;j++){

            if (C1[j][0]==i || C1[j][1]==i || C1[j][2]==i)
            {

                Nse[i]+=1;

            }

        }

        if(Nse[i]>Nem)
        {

            Nem=Nse[i];

        }

    }

    int C2[Np][Nem];    // Elements shared by each node
    int C3[Np][2*Nem];  // Nodes shared by each node

    for (int i=0;i<Np;i++){
        for (int j=0;j<2*Nem;j++)
        {
            C3[i][j]=-1;
        }
    }

    for (int i=0;i<Np;i++){
        for (int j=0;j<Nem;j++){
            C2[i][j]=-1;
        }
    }

    for (int i=0;i<Np;i++){

    temp=0;

        for (int j=0;j<Ne;j++){

            if (C1[j][0]==i || C1[j][1]==i || C1[j][2]==i)
            {

                C2[i][temp]=j;
            //     printf("%d %d\n",i,j);

                if (C1[j][0]==i)
                    {

                    C3[i][2*temp]=C1[j][1];
                    C3[i][2*temp+1]=C1[j][2];

                    }


                else if (C1[j][1]==i)
                    {

                    C3[i][2*temp]=C1[j][0];
                    C3[i][2*temp+1]=C1[j][2];

                    }


                else
                    {

                    C3[i][2*temp]=C1[j][1];
                    C3[i][2*temp+1]=C1[j][0];

                    }

                    temp+=1;

            }

        }

    }

// Calculate effective area of a node using area of shared triangles

    for (int i=0;i<Np;i++){
        Area=0;
        for (int j=0;j<Nem;j++){
            if(C3[i][2*j]!=-1 && C3[i][2*j+1]!=-1)
            {

            Area+=0.333*fabs(0.5*(Xr[i]*(Yr[C3[i][2*j]]-Yr[C3[i][2*j+1]])+Xr[C3[i][2*j]]*(Yr[C3[i][2*j+1]]-Yr[i])+Xr[C3[i][2*j+1]]*(Yr[i]-Yr[C3[i][2*j]])));

            }
        }

        Q0[i]=(density*Area/pow(dt,2))+(c/(2*dt));
        Q1[i]=(2*density*Area)/(pow(dt,2)*Q0[i]);
        Q2[i]=((density*Area/pow(dt,2))-(c/(2*dt)))/Q0[i];


    }

    N=0;

    while(N<Nt){

        printf("Time step is %d\n",N);



        for (int i=0;i<Np;i++){

            Fx[i]=0.0;
            Fy[i]=0.0;

        }

        // Force calculation

        for (int i=0;i<Np;i++){

        //printf("1 is %d %f %f\n",i,Fx[i],Fy[i]);

            for (int j=0;j<Nem;j++){

                if(C3[i][2*j]!=-1 && C3[i][2*j+1]!=-1)
                {
                    //**************** Formulation based on Plane stress

                    XD = X[i];
                    YD = Y[i];
                    XR = Xr[i];
                    YR = Yr[i];
                    XDv = X[C3[i][2*j]];
                    YDv = Y[C3[i][2*j]];
                    XRv = Xr[C3[i][2*j]];
                    YRv = Yr[C3[i][2*j]];
                    XDh = X[C3[i][2*j+1]];
                    YDh = Y[C3[i][2*j+1]];
                    XRh = Xr[C3[i][2*j+1]];
                    YRh = Yr[C3[i][2*j+1]];


                    P = XDh-XD;
                    Q = YDh-YD;
                    R = XRh-XR;
                    S = YRh-YR;
                    T = XDv-XD;
                    U = YDv-YD;
                    V = XRv-XR;
                    W = YRv-YR;

                    //**************************************** Calculation of Strain

                    EXX = (pow((P*W - S*T),2) +pow((Q*W - S*U),2))/(2.0*pow((R*W-S*V),2)) -1.0/2.0;
                    EYY = (pow((R*T - P*V),2) +pow((R*U - Q*V),2))/(2.0*pow((R*W-S*V),2)) -1.0/2.0;
                    EXY = ((R*T - P*V)*(P*W - S*T) + (R*U - Q*V)*(Q*W - S*U)) / (2.0*pow((R*W-S*V),2));


                    //***************************************Calculation of stress

                    ZXX = E*EXX/(1-pow(Nu,2))+E*Nu*EYY/(1-pow(Nu,2));
                    ZYY = E*EYY/(1-pow(Nu,2))+E*Nu*EXX/(1-pow(Nu,2));
                    ZXY = G*EXY;
                    

                    // SED = 0.5*(EXX*ZXX + EYY*ZYY + EXY*ZXY);

                    if (SED >= SEDmin){
                        // Elements[N*Ne + C2[i][j]] = 0;
                        continue;
                    }
                    //sig[i]+=sqrt(pow(ZXX,2)+pow(ZYY,2)-ZXX*ZYY+3*pow(ZXY,2));
                    //******************************** Derivative of strain

                    EYY_X = ((XRh-XRv)*(P*V - T*R))/pow((R*W-V*S),2);
                    EYY_Y = ((XRv-XRh)*(R*U - Q*V))/pow((R*W-V*S),2);
                    EXX_X = ((YRh-YRv)*(P*W - T*S))/pow((R*W-V*S),2);
                    EXX_Y = ((YRh-YRv)*(Q*W - S*U))/pow((R*W-V*S),2);
                    EXY_X = ((YRh-YRv)*(R*T - P*V) + (XRv-XRh)*(P*W - T*S))/(2.0*pow((R*W - V*S),2));
                    EXY_Y = ((XRv-XRh)*(Q*W - U*S) + (YRh-YRv)*(R*U - Q*V))/(2.0*pow((R*W - V*S),2));


                    //******************************** Derivative of stress

                    ZXX_X = E*EXX_X/(1-pow(Nu,2)) + E*Nu*EYY_X/(1-pow(Nu,2));
                    ZXX_Y = E*EXX_Y/(1-pow(Nu,2)) + E*Nu*EYY_Y/(1-pow(Nu,2));
                    ZYY_X = E*EYY_X/(1-pow(Nu,2)) + E*Nu*EXX_X/(1-pow(Nu,2));
                    ZYY_Y = E*EYY_Y/(1-pow(Nu,2)) + E*Nu*EXX_Y/(1-pow(Nu,2));
                    ZXY_X = G*EXY_X;
                    ZXY_Y = G*EXY_Y;


                    //******************************* Force calculation


                    Area = fabs(0.5*(XR*(YRh-YRv)+XRh*(YRv-YR)+XRv*(YR-YRh)));


                    Fx[i] += -Area*0.5*(ZXX_X*EXX + ZXX*EXX_X + ZYY_X*EYY + ZYY*EYY_X + 4*ZXY_X*EXY +    4*ZXY*EXY_X);

                    Fy[i] += -Area*0.5*(ZXX_Y*EXX + ZXX*EXX_Y + ZYY_Y*EYY + ZYY*EYY_Y + 4*ZXY_Y*EXY + 4*ZXY*EXY_Y);

                }

            }
        // printf("2 is %d %f %f\n",i,Fx[i],Fy[i]);
        }

        // Loading conditions
        for(int i=0;i<Np;i++){
            
            Fx[i] +=  N*(LC[i*4 + 2]/Nt);
            Fy[i] +=  N*(LC[i*4 + 3]/Nt);

        }

        

        // Update the positiosn after applying force
        for (int i=0;i<Np;i++)
        {
            //Boundary condition
            if(BC[i*3 + 2] == 0){
                // printf("BC %f\n", BC[i*3 + 2]);
                X[i] = (Fx[i]/Q0[i])+(Q1[i]*X[i])-(Q2[i]*X[i]);
                Y[i] = (Fy[i]/Q0[i])+(Q1[i]*Y[i])-(Q2[i]*Y[i]);   
            }
        }

        //Positions at timestep N
        for (int i=0;i<Np;i++){
            Positions[2*Np*N + 2*i] = X[i];
            Positions[2*Np*N + 2*i + 1] = Y[i];
        }
        

        N+=1;

    }

} 
