package io.mosip.ivv.registration.methods;

import io.mosip.ivv.core.base.Step;
import io.mosip.ivv.core.base.StepInterface;
import io.mosip.ivv.core.structures.ExtentLogger;
import io.mosip.ivv.core.structures.Scenario;
import io.mosip.ivv.core.structures.Store;
import io.mosip.ivv.core.utils.Utils;
import io.mosip.registration.context.SessionContext;
import io.mosip.registration.dto.RegistrationDTO;
import io.mosip.registration.dto.biometric.BiometricInfoDTO;
import io.mosip.registration.dto.biometric.FaceDetailsDTO;
import io.mosip.registration.dto.biometric.FingerprintDetailsDTO;
import io.mosip.registration.dto.biometric.IrisDetailsDTO;

import java.util.ArrayList;
import java.util.List;

public class OperatorAuthentication extends Step implements StepInterface {

    /**
     * Method to create RegistrationDTO if not created and adding only demographic details to it.
     * @param step
     */
    @Override
    public void run(Scenario.Step step) {
        RegistrationDTO registrationDTO = (RegistrationDTO) this.store.getRegistrationDto();
        BiometricInfoDTO biometricInfoDTO = new BiometricInfoDTO();
        biometricInfoDTO.setFace(this.getFace());
        biometricInfoDTO.setIrisDetailsDTO(this.getIris());
        biometricInfoDTO.setFingerprintDetailsDTO(this.getFingetprint());
        //TODO add applicant's biometric data in biometricInfoDTO

        registrationDTO.getBiometricDTO().setOperatorBiometricDTO(biometricInfoDTO);
        this.store.setRegistrationDto(registrationDTO);
    }

    private FaceDetailsDTO getFace(){
        FaceDetailsDTO dt = new FaceDetailsDTO();
        dt.setQualityScore(8);
        dt.setPhotographName("face");
        byte [] file = Utils.readFileAsByte(store.getScenarioData().getOperator().getFace().getPath());
        dt.setFaceISO(file);
        return dt;
    }

    private List<IrisDetailsDTO> getIris(){
        List<IrisDetailsDTO> ls = new ArrayList<>();

        /* left iris */
        IrisDetailsDTO lt = new IrisDetailsDTO();
        lt.setIrisType("LEFT");
        lt.setQualityScore(8);
        lt.setIrisImageName("left iris");
        byte [] lfile = Utils.readFileAsByte(store.getScenarioData().getOperator().getLeftIris().getPath());
        lt.setIrisIso(lfile);

        /* right iris */
        IrisDetailsDTO rt = new IrisDetailsDTO();
        rt.setIrisType("RIGHT");
        rt.setQualityScore(8);
        rt.setIrisImageName("left iris");
        byte [] rfile = Utils.readFileAsByte(store.getScenarioData().getOperator().getRightIris().getPath());
        rt.setIrisIso(rfile);

        ls.add(lt);
        ls.add(rt);
        return ls;
    }

    private List<FingerprintDetailsDTO> getFingetprint(){
        List<FingerprintDetailsDTO> ls = new ArrayList<>();

//        /* left slap */
//        FingerprintDetailsDTO lf = new FingerprintDetailsDTO();
//        lf.setFingerType("Left");
//        lf.setQualityScore(8);
//        lf.setFingerprintImageName("left finger");
//        lf.setFingerPrint(Utils.readFileAsByte(store.getScenarioData().getOperator().getLeftSlap().getPath()));
//
//        /* right slap */
//        FingerprintDetailsDTO rf = new FingerprintDetailsDTO();
//        rf.setFingerType("Right");
//        rf.setQualityScore(8);
//        rf.setFingerprintImageName("right finger");
//        rf.setFingerPrint(Utils.readFileAsByte(store.getScenarioData().getOperator().getRightSlap().getPath()));

        /* thumb */
        FingerprintDetailsDTO tb = new FingerprintDetailsDTO();
        tb.setFingerType("leftThumb");
        tb.setQualityScore(8);
        tb.setFingerprintImageName("left thumb");
        byte [] tbfile = Utils.readFileAsByte(store.getScenarioData().getOperator().getThumbs().getPath());
        tb.setFingerPrintISOImage(tbfile);
        tb.setSegmentedFingerprints(new ArrayList<FingerprintDetailsDTO>());
//        ls.add(lf);
//        ls.add(rf);
        ls.add(tb);

        return ls;
    }
}